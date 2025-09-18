import time
from multiprocessing.managers import DictProxy
from queue import Empty
from typing import List, Optional

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket

from .generic import GenericPipe


class TimeBatchPipe(GenericPipe[InPacket, List[InPacket]]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[List[InPacket]]",
        time_interval: float,
    ):
        self._interval: float = time_interval
        self._timeout: float = time_interval
        self._datas: List[InPacket] = []
        self._last_time = time.time()
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"TBatch:{self._interval}s"

    def _perform_task(self, data: InPacket) -> Optional[List[InPacket]]:  # type: ignore
        elapsed = time.time() - self._last_time
        self._timeout = self._last_time + self._interval - time.time()
        if elapsed >= self._interval:
            self.increment_timeout()
            packet = self._datas[:]
            self._datas.clear()
            self._datas.append(data)
            return packet
        self._datas.append(data)
        return None

    def increment_timeout(self):
        self._last_time += self._interval
        self._timeout += self._interval

    def _send_to_next(self, processed: List[InPacket]):
        super()._send_to_next(processed)

    def run(self):
        while True:
            try:
                data = self.get_next()
                processed = self._perform_task(data)
                if processed is not None:
                    self._send_to_next(processed)
            except Empty:
                pass
            except TimeoutError:
                self._send_to_next(self._datas)
                self._datas = []
            except Exception as e:
                print(self.__repr__(), "Error", e)
                self.set_error_mode()
            if self.can_quit():
                self._send_to_next(self._datas)
                self._kill()
                break
