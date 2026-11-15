"""A fake payment gateway, with a switch to make it go down on stage.

Turn the outage on and off with:
    python chaos.py down
    python chaos.py up

Like many real (old) SDKs, refund() behaves badly when you don't pass a
timeout: it hangs for a while and then quietly returns None instead of
raising an error. Pass timeout=... and it raises TimeoutError instead.
"""

import time
import uuid
from dataclasses import dataclass
from pathlib import Path

DOWN_FLAG = Path(__file__).resolve().parent.parent / "payments_down.flag"
HANG_SECONDS = 2  # how long a "timeout" takes on stage; tests set this to 0


@dataclass
class Transaction:
    id: str
    order_id: str
    amount: float


def is_down() -> bool:
    return DOWN_FLAG.exists()


def refund(order_id: str, amount: float, timeout: float | None = None) -> Transaction | None:
    if is_down():
        time.sleep(HANG_SECONDS)
        if timeout is None:
            return None  # the silent failure: no error, no money moved
        raise TimeoutError(f"Payment gateway did not respond within {timeout}s")
    return Transaction(id="TXN-" + uuid.uuid4().hex[:8].upper(), order_id=order_id, amount=amount)
