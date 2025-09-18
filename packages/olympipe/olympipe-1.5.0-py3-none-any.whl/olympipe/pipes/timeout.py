from multiprocessing.managers import DictProxy
import time
from typing import List, cast


from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket

from .generic import GenericPipe


class TimeoutPipe(GenericPipe[InPacket, InPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[InPacket]",
        timeout: float,
    ):
        self._seen_timeout: float = timeout
        self._last_time_seen: float = time.time()
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"Timeout:{self._seen_timeout}"

    def get_next(self) -> InPacket:
        if time.time() > self._last_time_seen + self._seen_timeout:
            self.set_error_mode()
            self._kill()
            raise Exception("Timeout")
        return cast(InPacket, self._source_queue.get(timeout=self._seen_timeout))
