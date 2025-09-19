import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

import websockets
import websockets.protocol

from .connection_mixin import ConnectionMixin
from .decorators import DecoratorMixin
from .extra.zmq import ZMQMixin
from .message_processing import MessageProcessingMixin
from .protocol import ClientProtocol
from .schema.items import AnyItem
from .tick_loop import TickLoopMixin
from .utils.item_cache import ItemStorageMixin

if TYPE_CHECKING:
    from .db import DBClient
import logging
from collections import defaultdict

from .schema.events import AnyEvent
from .schema.intents import AnyIntent
from .structure.game_state import GameState
from .structure.instance import Instance
from .structure.on_tick_response import (
    OnTickResponse,
)

logger = logging.getLogger(__name__)


try:
    from .db import DBClient

    _db_available = True
except ImportError:
    DBClient = type(None)  # type: ignore
    _db_available = False

OnLoopHandler = Callable[[GameState], Coroutine[Any, Any, AnyIntent | None]]
OnEventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]
OnLoopHandlerWithEvents = Callable[[GameState, list[AnyEvent]], Coroutine[Any, Any, AnyIntent | None]]

CallableScript = Callable[[], Coroutine[Any, Any, "OnTickResponse"]]
OnSetupCharacter = Callable[[GameState], Coroutine[Any, Any, Any | CallableScript]]


# noinspection PyPep8Naming
class GameClient(
    DecoratorMixin, MessageProcessingMixin, ConnectionMixin, ItemStorageMixin, TickLoopMixin, ZMQMixin
):
    _central_task: asyncio.Task[None] | None = None
    context_managers: list[Any] = None

    def __init__(
        self: ClientProtocol,
        *,
        log_level: str = "INFO",
        enable_db: bool = False,
        database_url: str | None = None,
        disable_loop: bool = False,
        **kwargs,
    ):
        self._log_level = log_level
        self._websocket: websockets.WebSocketClientProtocol | None = None  # type: ignore
        self._time = 0
        self.instances: dict[str, Instance] = {}
        self._items: dict[str, AnyItem] = {}
        self._constants: Any = {}
        self._is_running = False
        self._reconnect_delay = 1

        self._disable_loop: bool = disable_loop

        self._server_version: str | None = None
        self._client_version: str | None = None

        self._setup_character_handler: dict[str, Any] | None = None
        self._on_event_handlers: dict[
            type[AnyEvent], list[Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]]
        ] = defaultdict(list)

        super().__init__(**kwargs)

        # Optional DB integration
        self._db_client: DBClient | None = None
        if enable_db and _db_available:
            self._db_client = DBClient(self._config.DATABASE_URL)
        elif enable_db and not _db_available:
            logger.warning(
                "DB integration requested but dependencies not installed. Install with: pip install programming-game[db]"
            )

    # DB integration methods
    async def get_db_session(self) -> Any:
        """Get a database session for user operations."""
        if self._db_client:
            return await self._db_client.get_session()
        else:
            raise RuntimeError("Database integration not enabled. Set enable_db=True in constructor.")

    async def queue_event(self, event_data: dict[str, Any], user_id: str | None = None):
        """Queue a user-defined event for logging to database."""
        if self._db_client:
            await self._db_client.queue_user_event(event_data, user_id)
        else:
            logger.warning("Database integration not enabled. Event not queued.")
