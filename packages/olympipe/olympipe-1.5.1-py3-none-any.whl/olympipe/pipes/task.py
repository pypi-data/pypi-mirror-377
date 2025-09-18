from multiprocessing.managers import DictProxy
from typing import Callable, List

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket, OutPacket

from .generic import GenericPipe


class TaskPipe(GenericPipe[InPacket, OutPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        task: Callable[[InPacket], OutPacket],
        target: "ShuttableQueue[OutPacket]",
    ):
        self._task = task
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return self._task.__name__

    def _perform_task(self, data: InPacket) -> OutPacket:
        return self._task(data)
