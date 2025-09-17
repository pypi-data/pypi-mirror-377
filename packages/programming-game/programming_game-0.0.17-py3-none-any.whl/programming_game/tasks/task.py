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

    async def __call__(self, *, game_state, events, **kwargs):
        start = time.time()
        self.gs = game_state
        self.events = events

        if self._sub_task:
            if result := await self._sub_task(game_state=game_state, events=events, **kwargs):
                if result is True:
                    return None
                return result
            logger.debug("Subtask finished", self._sub_task)
            self._sub_task = None
            return TickPause(0.005)

        if self._on_tick_method:
            for handler in self._on_tick_method:
                interval = getattr(handler, "_interval", None)
                if interval is not None and start - handler._last_run < interval:
                    continue
                handler._last_run = start
                if result := await handler(self):
                    if isinstance(result, Task):
                        self._sub_task = result
                        return TickPause(0.005)
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
