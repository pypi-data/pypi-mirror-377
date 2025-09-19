from multiprocessing.managers import DictProxy
from queue import Empty
from typing import List, Optional

from olympipe.pipes.generic import GenericPipe
from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket


class BatchPipe(GenericPipe[InPacket, List[InPacket]]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[List[InPacket]]",
        batch_size: int,
        keep_incomplete_batch: bool,
    ):
        self._batch_size = batch_size
        self._datas: List[InPacket] = []
        self._keep_incomplete_batch = keep_incomplete_batch
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"Batch:{self._batch_size}"

    def _perform_task(self, data: InPacket) -> Optional[List[InPacket]]:  # type: ignore
        self._datas.append(data)
        if len(self._datas) >= self._batch_size:
            packet, self._datas = (
                self._datas[: self._batch_size],
                self._datas[self._batch_size :],
            )
            return packet

    def _send_to_next(self, processed: Optional[List[InPacket]]) -> None:
        if processed is None:
            return
        super()._send_to_next(processed)

    def run(self):
        while True:
            try:
                data = self.get_next()
                processed = self._perform_task(data)
                self._send_to_next(processed)
            except (Empty, TimeoutError):
                pass
            except Exception as e:
                print(self.__repr__(), "Error", e)
                self.set_error_mode()
            if self.can_quit():
                if self._keep_incomplete_batch and len(self._datas) > 0:
                    self._send_to_next(self._datas)
                self._kill()
                break
