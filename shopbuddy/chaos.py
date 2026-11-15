"""Switch the fake payment gateway on and off during the talk (Problem 3).

    python chaos.py down     # refunds now time out
    python chaos.py up       # back to normal
    python chaos.py          # show the current state

Works while `adk web` is running; no restart needed.
"""

import sys

from shopkart.payments import DOWN_FLAG

cmd = sys.argv[1].lower() if len(sys.argv) > 1 else "status"
if cmd == "down":
    DOWN_FLAG.write_text("payments are down\n")
elif cmd == "up":
    DOWN_FLAG.unlink(missing_ok=True)
elif cmd != "status":
    sys.exit("Usage: python chaos.py [down|up]")

print("Payment gateway is", "DOWN ❌ (refunds will time out)" if DOWN_FLAG.exists() else "UP ✅")
