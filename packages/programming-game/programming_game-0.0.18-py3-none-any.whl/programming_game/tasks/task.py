import time
from collections.abc import Awaitable, Callable
from typing import Any

from loguru import logger

from programming_game.structure.on_tick_response import OnTickResponse, TickPause
from programming_game.tasks.task_meta import TaskMeta


class Task(metaclass=TaskMeta):
    _sub_task: "Task | None" = None

    @staticmethod
    def on_tick(*, interval: float | None = None) -> Callable[[Callable], Callable]:
        """
        Ein parametrisierter Decorator zum Markieren einer asynchronen on_tick-Methode.

        Parameter:
            name: Ein optionaler Name für die Aufgabe.
        """

        def decorator(
            func: Callable[[Any], Awaitable[OnTickResponse]],
        ) -> Callable[[Any], Awaitable[OnTickResponse]]:
            """Der eigentliche Decorator, der die Funktion umhüllt."""
            func._on_tick_method = True
            func.interval = interval
            return func

        return decorator

    @staticmethod
    def on_event(event_filter: Any = None) -> Callable[[Callable], Callable]:
        """
        Ein Decorator zum Markieren einer asynchronen on_event-Methode.
        Diese Methode wird aufgerufen, wenn Events vorhanden sind, bevor on_tick-Methoden ausgeführt werden.

        Parameter:
            event_filter: Optional filter für Events (z.B. MovedEvent oder (MovedEvent, CaloriesEvent)).
                          Wenn None, wird die Methode für alle Events aufgerufen.
        """

        def decorator(
            func: Callable[[Any, Any], Awaitable[None]],
        ) -> Callable[[Any, Any], Awaitable[None]]:
            """Der eigentliche Decorator, der die Funktion umhüllt."""
            func._on_event_method = True
            func._event_filter = event_filter
            return func

        return decorator

    async def _handle_return(self, result):
        if isinstance(result, Task):
            self._sub_task = result
            return TickPause(0.005)
        return result

    async def __call__(self, *, game_state, events, **kwargs):
        start = time.time()
        self.gs = game_state
        self.events = events

        if self._sub_task:
            if result := await self._sub_task(game_state=game_state, events=events, **kwargs):
                if result is True:
                    logger.debug("Subtask finished", self._sub_task)
                    self._sub_task = None
                    return TickPause(0.005)
                return result

        if self._on_event_method:
            for handler, event_filter in self._on_event_method:
                if event_filter is None:
                    await handler(self, events)
                else:
                    filtered_events = [event for event in events if isinstance(event, event_filter)]
                    if filtered_events:
                        await handler(self, filtered_events)

        if self._on_tick_method:
            for handler in self._on_tick_method:
                interval = getattr(handler, "_interval", None)
                if interval is not None and start - handler._last_run < interval:
                    continue
                handler._last_run = start
                if result := await self._handle_return(await handler(self)):
                    return result

        return None

    def set_subtask(self, param):
        self._sub_task = param
        logger.debug("New Subtask {}", type(self._sub_task))

    @property
    def player(self):
        return self.gs.player

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.player.name})>"
