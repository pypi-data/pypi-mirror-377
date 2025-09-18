from multiprocessing.managers import DictProxy
from typing import Callable, List, Optional

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket

from .generic import GenericPipe


class FilterPipe(GenericPipe[InPacket, InPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        keep_if_true: Optional[Callable[[InPacket], bool]],
        target: "ShuttableQueue[InPacket]",
    ):
        self._keep_if_true = self.filter_none if keep_if_true is None else keep_if_true
        super().__init__(father_process_dag, source, target)

    @staticmethod
    def filter_none(packet: InPacket) -> bool:
        return packet is not None

    @property
    def shortname(self) -> str:
        return f"filter:{self._keep_if_true.__name__}"

    def _perform_task(self, data: InPacket) -> InPacket:
        if self._keep_if_true(data):
            super()._send_to_next(data)
        return data

    def _send_to_next(self, processed: InPacket):
        pass
