from multiprocessing.managers import DictProxy
from typing import List

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket

from .generic import GenericPipe


class DebugPipe(GenericPipe[InPacket, InPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[InPacket]",
    ):
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return "_"

    def _perform_task(self, data: InPacket) -> InPacket:
        print(self.__repr__().replace("_", str(self.pid)), data)
        return data
