import hashlib
import string
import uuid
from multiprocessing import Value, get_context
from multiprocessing.queues import Queue
from typing import Generic, TypeVar

R = TypeVar("R")


class ShuttableQueue(Queue, Generic[R]):
    _max_queue_size = 4

    def __init__(self) -> None:
        ctx = get_context()
        super().__init__(ShuttableQueue._max_queue_size, ctx=ctx)
        self.pid = self.create_id()
        self._shut = Value("b", False)

    def create_id(self):
        CHARS = string.ascii_uppercase + string.ascii_lowercase + string.digits
        BASE = len(CHARS)

        def base62_encode(num: int):
            """Encode a number in Base62."""
            if num == 0:
                return CHARS[0]
            arr = []
            while num:
                num, rem = divmod(num, BASE)
                arr.append(CHARS[rem])
            arr.reverse()
            return "".join(arr)

        def generate_short_uuid():
            """Generate a short UUID."""
            # Create a UUID
            uid = uuid.uuid4()

            # Hash the UUID with SHA-256
            hash_val = hashlib.sha256(uid.bytes).digest()

            # Convert the hash to a number
            num = int.from_bytes(hash_val, "big")

            # Base62 encode the number to get a shorter string
            return base62_encode(num)[:8]

        return "Q-" + generate_short_uuid()
