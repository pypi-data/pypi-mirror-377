from multiprocessing.managers import BaseManager, DictProxy
from typing import Any, Callable, Dict, List, Optional, Type

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import ClassType, InPacket, OutPacket

from .generic import GenericPipe


class ClassInstancePipe(GenericPipe[InPacket, OutPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        class_constructor: Type[ClassType],
        class_method: Callable[[ClassType, InPacket], OutPacket],
        target: "ShuttableQueue[OutPacket]",
        close_method: Optional[Callable[[ClassType], Any]] = None,
        class_args: Optional[List[Any]] = None,
        class_kwargs: Optional[Dict[str, Any]] = None,
    ):
        BaseManager.register(class_constructor.__name__, class_constructor)
        self._class_constructor = class_constructor
        self._class_method = class_method
        self._close_method = close_method
        self._class_args = class_args or []
        self._class_kwargs = class_kwargs or {}
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"{self._class_constructor.__name__}:{self._class_method.__name__}"

    def start(self) -> None:
        self._instance = self._class_constructor(
            *self._class_args, **self._class_kwargs
        )
        self._task = getattr(self._instance, self._class_method.__name__)
        if self._close_method is not None:
            self._close_method = getattr(self._instance, self._close_method.__name__)
        else:
            self._close_method = None
        return super().start()

    def _perform_task(self, data: InPacket) -> OutPacket:
        return self._task(data)

    def _kill(self):
        if self._close_method is not None:
            self._close_method()  # type: ignore
        super()._kill()
