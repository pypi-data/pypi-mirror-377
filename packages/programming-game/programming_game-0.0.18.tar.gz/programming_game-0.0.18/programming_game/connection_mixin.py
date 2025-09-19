import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any

import msgspec
import websockets
import websockets.exceptions
import websockets.protocol

from .protocol import ClientProtocol
from .schema.events import AnyEvent

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass
logger = logging.getLogger(__name__)

json_encoder = msgspec.json.Encoder()
json_decoder = msgspec.json.Decoder()


class ConnectionMixin(ClientProtocol):
    """
    Mixin für WebSocket-Verbindungsmanagement, Authentication und Reconnection-Logik.

    Folgt dem Muster der bestehenden Mixins (z.B. MessageProcessingMixin, DecoratorMixin):
    - Bietet Methoden für Connection-Handling bereit.
    - Nahtlose Integration durch Vererbung in GameClient.
    - Abhängigkeiten: self._websocket, self._is_running, self._reconnect_delay, self._config, self._db_client.
    - Verwendet AsyncExitStack für Context Managers und exponential backoff für Reconnects.
    """

    def __init__(self, **kwargs):
        self.context_managers = []
        super().__init__(**kwargs)

    async def _send(self, message: dict[str, Any]) -> None:
        """Sendet eine rohe Dictionary-Nachricht über WebSocket."""
        if self._websocket:
            msg_str = json_encoder.encode(message).decode("utf-8")
            await self._websocket.send(msg_str)

    async def _send_msg(self, data: msgspec.Struct) -> None:
        """Sendet eine msgspec.Struct-Nachricht über WebSocket."""
        if self._websocket:
            msg_str = json_encoder.encode(data).decode("utf-8")
            # logger.debug(f"message: {msg_str}")
            await self._websocket.send(msg_str)

    async def connect(
        self: ClientProtocol,
        user_id: str,
        user_key: str,
        websocket_url: str = "wss://programming-game.com",
        on_connected: Callable[[], Awaitable[None]] | None = None,
        on_event: Callable[[str, str, AnyEvent], Awaitable[None]] | None = None,
    ) -> None:
        """Stellt die WebSocket-Verbindung her, handhabt Authentication und Reconnects."""
        self._user_id = user_id
        await self.load_items_and_constants()

        if not self._setup_character_handler and not self._disable_loop:
            raise RuntimeError(
                "No setup_character handler registered. Use @client.setup_character decorator or disable loop in configuration."
            )
        self._is_running = True
        self._on_event = on_event

        # Initialize DB if enabled
        if self._db_client:
            await self._db_client.initialize()

        async with AsyncExitStack() as stack:
            logger.debug(f"Context managers: {self.context_managers}")
            for manager in self.context_managers:
                logger.debug(f"Manager type: {type(manager)}, callable: {callable(manager)}")
                await stack.enter_async_context(manager)

            while self._is_running:
                logger.info(f"Connecting to server at {websocket_url}...")
                try:
                    async with websockets.connect(
                        websocket_url, ping_timeout=30
                    ) as websocket:  # TODO: check ping_timeout
                        self._websocket = websocket
                        self._reconnect_delay = 1  # Reset reconnect delay on successful connection
                        logger.debug("Connection established successfully!")
                        await self._send(
                            {
                                "type": "credentials",
                                "value": {"id": user_id, "key": user_key},
                                "version": self._client_version or "0.0.1",
                            }
                        )
                        self.is_connected = True
                        if on_connected:
                            await on_connected()
                        if not self._disable_loop:
                            # Delegate to TickLoopMixin
                            loop = self._central_tick_loop()
                            self._central_task = asyncio.create_task(loop)

                        async for message_str in websocket:
                            if self._zmq_enabled:
                                await self.zmq_push_event(message_str)
                            if message := self.parse_message(message_str):
                                await self.handle_message(message)

                except websockets.exceptions.ConnectionClosed as e:
                    logger.warning(
                        f"Connection closed: {e}. Reconnecting in {self._reconnect_delay} seconds..."
                    )
                except ConnectionRefusedError:
                    logger.error(
                        f"Connection refused. Reconnecting in {self._reconnect_delay} seconds...",
                        exc_info=True,
                    )
                except Exception:
                    logger.error(
                        f"A critical error occurred. Reconnecting in {self._reconnect_delay} seconds...",
                        exc_info=True,
                    )
                finally:
                    # Cancel central tick task on disconnect
                    if self._central_task and not self._central_task.done():
                        self._central_task.cancel()

                    # Reset runtime data for characters
                    for instance in self.instances.values():
                        for character in instance.characters.values():
                            character.last_intent_time = 0.0

                    # Clear instances to prevent memory leak on reconnect
                    logger.debug(f"Clearing _instances with {len(self.instances)} instances")
                    self.instances.clear()
                    logger.debug("_instances cleared")

                    self._websocket = None
                    if self._is_running:
                        await asyncio.sleep(self._reconnect_delay)
                        self._reconnect_delay = min(
                            self._reconnect_delay * 2, 60
                        )  # Exponential backoff, max 60s

    async def disconnect(self: ClientProtocol) -> None:
        """Gracefully disconnects from the server."""
        # logger.info("Disconnecting from server...")
        self._is_running = False
        self.is_connected = False
        # Cancel central task
        if self._central_task and not self._central_task.done():
            self._central_task.cancel()

        # Reset runtime data for characters
        self.instances.clear()

        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            await self._websocket.close()
        self._websocket = None

        # Shutdown DB client
        if self._db_client:
            await self._db_client.shutdown()

        logger.info("Disconnected successfully.")
