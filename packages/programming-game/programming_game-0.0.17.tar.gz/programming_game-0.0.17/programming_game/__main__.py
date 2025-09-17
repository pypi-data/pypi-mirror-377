import asyncio
import importlib
import logging
import os
import signal
import subprocess
import sys
import time

import click
from dotenv import dotenv_values
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


# Add current working directory to the Python path
# This allows us to import from a local bot_logic directory
sys.path.insert(0, os.getcwd())


async def run_bot(
    script_module: str,
    debug: bool = False,
    logging: bool = False,
    no_rich_logging: bool = False,
    user_id: str = None,
    user_key: str = None,
    websocket_url: str = None,
):
    """
    Initializes and runs the game client with the specified script.
    """

    try:
        module_name, instance_name = script_module.split(":", 1)
    except ValueError:
        logger.error(
            f"Invalid script format: '{script_module}'. Please use the format 'module.path:instance_name'."
        )
        return

    if logging:
        from .logging import setup_logging

        setup_logging(debug, no_rich_logging)
        logger.info(f"Logging handler added. (debug: {str(debug)}, rich_logging: {str(not no_rich_logging)})")

    module = importlib.import_module(module_name)
    client = getattr(module, instance_name)

    loop = asyncio.get_running_loop()

    async def shutdown(sig: signal.Signals):
        logger.warning(f"Received shutdown signal: {sig.name}")
        if client:
            await client.disconnect()

        # Cancel all remaining tasks
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete, but don't wait indefinitely
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=2.0)
        except TimeoutError:
            logger.warning("Some tasks did not complete within timeout, forcing shutdown")
        except RuntimeError as e:
            if "Event loop stopped before Future completed" in str(e):
                logger.warning("Event loop stopped during shutdown, this is expected during reload")
            else:
                logger.error(f"Unexpected error during shutdown: {e}")

        # Don't call loop.stop() as it can cause issues during reload  # The event loop will be stopped by the subprocess termination

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s)))

    config = {
        **dotenv_values(".env"),  # load shared development variables
        **os.environ,  # override loaded values with environment variables
    }

    if user_id:
        config["GAME_CLIENT_ID"] = user_id
    if user_key:
        config["GAME_CLIENT_KEY"] = user_key
    if websocket_url:
        config["WEBSOCKET_URL"] = websocket_url

    try:
        await client.connect(
            user_id=config.get("GAME_CLIENT_ID"),
            user_key=config.get("GAME_CLIENT_KEY"),
            websocket_url=config.get("WEBSOCKET_URL"),
        )
    except asyncio.CancelledError:
        logger.info("Main client connection task was cancelled.")


@click.group()
def cli():
    """A command-line interface for the game client."""
    pass


class ChangeHandler(FileSystemEventHandler):
    """Handles file changes and triggers a restart of the bot process."""

    def __init__(
        self,
        script_module,
        debug=False,
        logging=False,
        no_rich_logging=False,
        user_id: str = None,
        user_key: str = None,
        websocket_url: str = None,
    ):
        self.script_module = script_module
        self.debug = debug
        self.process = None
        self.last_restart_time = 0
        self.debounce_period = 2  # Cooldown period in seconds
        self.enable_logging = logging
        self.no_rich_logging = no_rich_logging
        self.user_id = user_id
        self.user_key = user_key
        self.websocket_url = websocket_url

        self.start_process()

    def start_process(self):
        """Starts the main.py script as a subprocess."""
        if self.process and self.process.poll() is None:
            logger.info("Terminating existing bot process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)  # Increased timeout for graceful shutdown
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully within 10 seconds, killing it.")
                self.process.kill()
                try:
                    self.process.wait(timeout=2)  # Give it 2 more seconds after kill
                except subprocess.TimeoutExpired:
                    logger.error("Process still didn't terminate after kill signal")
            logger.info("Process terminated.")

        config = {
            **dotenv_values(".env"),  # load shared development variables
            **os.environ,  # override loaded values with environment variables
        }
        if self.user_id:
            config["GAME_CLIENT_ID"] = self.user_id
        if self.user_key:
            config["GAME_CLIENT_KEY"] = self.user_key
        if self.websocket_url:
            config["WEBSOCKET_URL"] = self.websocket_url
        command = [
            sys.executable,
            "-m",
            "programming_game",
            "run",
            self.script_module,
            "--user-id",
            config["GAME_CLIENT_ID"],
            "--user-key",
            config["GAME_CLIENT_KEY"],
            "--websocket",
            config["WEBSOCKET_URL"],
        ]

        if self.debug:
            command.append("--debug")
        if self.enable_logging:
            command.append("--logging")
        if self.no_rich_logging:
            command.append("--no-rich-logging")

        logger.debug("Starting new bot process... {}".format(" ".join(command)))
        self.process = subprocess.Popen(command)

    def on_any_event(self, event):
        logger.debug(f"Event received: type={event.event_type}, path='{event.src_path}'")

        # More robust filtering
        if (
            event.is_directory
            or not event.src_path.endswith(".py")
            or "__pycache__" in event.src_path
            or ".git" in event.src_path
            or os.path.basename(event.src_path).startswith(".")
        ):
            return

        current_time = time.time()
        if current_time - self.last_restart_time < self.debounce_period:
            return

        self.last_restart_time = current_time
        logger.warning(f"Detected '{event.event_type}' on file: '{event.src_path}'. Restarting bot...")
        self.start_process()

    def stop(self):
        """Stops the subprocess when the observer is stopped."""
        if self.process and self.process.poll() is None:
            logger.info("Stopping bot process...")
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("Process did not terminate gracefully, killing it.")
                self.process.kill()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logger.error("Process still didn't terminate after kill signal")


def run_with_reloader(
    script_module: str,
    paths_to_watch: list[str] = None,
    debug: bool = False,
    logging: bool = False,
    no_rich_logging: bool = False,
    user_id: str = None,
    user_key: str = None,
    websocket_url: str = None,
):
    """Main function to set up and run the file observer."""
    event_handler = ChangeHandler(
        script_module, debug, logging, no_rich_logging, user_id, user_key, websocket_url
    )
    observer = Observer()
    for path in paths_to_watch or []:
        observer.schedule(event_handler, path, recursive=True)
        logger.info(f"Watching for file changes in '{path}/'...")

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
    finally:
        event_handler.stop()
        observer.stop()
        observer.join()
        logger.info("Shutdown complete.")


@cli.command()
@click.argument("script_module")
@click.option("--reload", is_flag=True, help="Enable auto-reloading.")
@click.option("--debug", default=False, is_flag=True, help="Set the log level to DEBUG")
@click.option(
    "--websocket", default="wss://programming-game.com", help="Set the URL where to connect [WEBSOCKET_URL]"
)
@click.option(
    "--user-id",
    default="",
    help="User id can also be set in .env or as environment variable [GAME_CLIENT_ID]",
)
@click.option(
    "--user-key",
    default="",
    help="User key can also be set in .env or as environment variable [GAME_CLIENT_KEY]",
)
@click.option("--logging", default=False, is_flag=True, help="Add a logging handler to the console.")
@click.option("--no-rich-logging", default=False, is_flag=True, help="Disable rich (colorful) logging.")
def run(
    script_module: str,
    reload: bool,
    debug: bool,
    logging: bool,
    no_rich_logging: bool,
    user_id: str,
    user_key: str,
    websocket: str,
):
    """
    Runs the game client with the specified bot script.

    SCRIPT_MODULE: The Python module path to the bot script (e.g., bot_logic.example_bot).
    """
    if reload:
        # Directories to monitor for changes
        run_with_reloader(
            script_module,
            [os.getcwd(), os.path.dirname(__file__)],
            debug,
            logging,
            no_rich_logging,
            user_id,
            user_key,
            websocket,
        )
    else:
        try:
            asyncio.run(run_bot(script_module, debug, logging, no_rich_logging, user_id, user_key, websocket))
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("Bot stopping...")
        finally:
            logger.info("Shutdown process complete.")


if __name__ == "__main__":
    cli()
