from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Protocol

from programming_game.schema.events import AnyEvent
from programming_game.schema.items import AnyItem
from programming_game.structure.game_state import GameState
from programming_game.structure.instance import Instance


class ClientProtocol(Protocol):
    # connection mixin
    _user_id: str | None = None
    _disable_loop: bool = False
    _setup_character_handler: dict[str, Any]
    _central_tick_loop: Any
    is_connected: bool = False
    context_managers: list[Any]
    _on_event: Callable[["ClientProtocol", str, str, AnyEvent], Awaitable[None]] | None
    _is_running: bool
    # loop config
    _fast_loop_delay: float = 0.1
    _slow_loop_delay: float = 0.3
    # zmq (optional)
    _zmq_enabled: bool = False

    async def zmq_push_event(self, message: str, channel: str | None = None): ...
    async def zmq_send_action(self, topic: str, action: str): ...
    async def zmq_send_binary(self, topic: str, data: bytes): ...

    # other
    instances: dict[str, Instance]
    _on_event_handlers: dict[type[AnyEvent], list[Callable[[AnyEvent, GameState], Coroutine[Any, Any, None]]]]
    _items: dict[str, AnyItem]
    _constants: dict[str, float | int | str]
    _server_version: str | None
    _client_version: str | None
