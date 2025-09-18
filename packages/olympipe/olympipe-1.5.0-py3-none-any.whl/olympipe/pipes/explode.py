from multiprocessing.managers import DictProxy
from typing import Callable, Iterable, List, Optional, cast

from olympipe.pipes.task import TaskPipe
from olympipe.shuttable_queue import ShuttableQueue
from olympipe.types import InPacket, OutPacket


class ExplodePipe(TaskPipe[InPacket, OutPacket]):
    def __init__(
        self,
        father_process_dag: "DictProxy[str, List[str]]",
        source: "ShuttableQueue[InPacket]",
        explode_function: Optional[Callable[[InPacket], Iterable[OutPacket]]],
        target: "ShuttableQueue[OutPacket]",
    ):
        explode_function = (
            (lambda x: cast(Iterable[OutPacket], x))
            if explode_function is None
            else explode_function
        )
        super().__init__(father_process_dag, source, explode_function, target)  # type: ignore

    @property
    def shortname(self) -> str:
        return f"explode:{self._task.__name__}"

    def _send_to_next(self, processed: Iterable[OutPacket]):  # type: ignore
        for p in processed:
            super()._send_to_next(p)
