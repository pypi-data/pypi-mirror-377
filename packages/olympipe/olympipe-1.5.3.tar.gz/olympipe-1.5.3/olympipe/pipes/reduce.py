from multiprocessing.managers import DictProxy
from queue import Empty
from typing import Callable, List

from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket, OutPacket

from .generic import GenericPipe


class ReducePipe(GenericPipe[InPacket, OutPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        target: "ShuttableQueue[OutPacket]",
        accumulator: OutPacket,
        reducer: Callable[[InPacket, OutPacket], OutPacket],
    ):
        self._accumulator = accumulator
        self._reduce_function = reducer
        super().__init__(father_process_dag, source, target)

    @property
    def shortname(self) -> str:
        return f"reduce:{self._reduce_function.__name__}"

    def _perform_task(self, data: InPacket) -> None:  # type: ignore
        self._accumulator = self._reduce_function(data, self._accumulator)

    def _kill(self):
        self._send_to_next(self._accumulator)
        super()._kill()

    def run(self):
        while True:
            try:
                data = self.get_next()
                self._perform_task(data)
            except (Empty, TimeoutError):
                pass
            except Exception as e:
                print(self.__repr__(), "Error", e)
                self.set_error_mode()
            if self.can_quit():
                self._kill()
                break
