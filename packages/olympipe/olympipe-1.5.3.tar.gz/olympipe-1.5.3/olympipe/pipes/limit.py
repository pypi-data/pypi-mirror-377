from multiprocessing.managers import DictProxy
from typing import List

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket

from .generic import GenericPipe


class LimitPipe(GenericPipe[InPacket, InPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[InPacket]",
        packet_limit: int,
    ):
        self._packet_limit: int = packet_limit
        self._seen: int = 0
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"Limit:{self._packet_limit}"

    def _perform_task(self, data: InPacket) -> InPacket:
        self._seen += 1

        if self._packet_limit > self._seen - 1:
            return data

        raise Exception(f"Limit of {self._packet_limit} packets attained")
