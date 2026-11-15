"""Run all four demo prompts against the broken and fixed agents and print what happened.

    python rehearse.py            # all problems
    python rehearse.py 3          # just problem 3

LLMs don't give the same answer every time. Run this a few times before the
talk (and on the venue Wi-Fi) so you know how each demo is likely to go.
"""

import asyncio
import sys

from shopkart import payments
from shopkart.run import has_api_key, run_once

DEMOS = {
    1: ("It makes things up",
        ["Hi! What's your return policy for electronics? Thinking of buying the BoomX headphones"]),
    2: ("It picks the wrong tool",
        ["Cancel my order for the blue running shoes", "ORD-10421"]),
    3: ("A tool fails silently",
        ["I returned the BoomX headphones last week. Refund please! ORD-10388"]),
    4: ("A review takes control",
        ["Summarise the reviews for the BoomX headphones in my cart (ORD-10500)."]),
}


def show(label: str, result: dict) -> None:
    print(f"\n  --- {label} ---")
    for name, args in result["calls"]:
        print(f"  \U0001F527 {name}({', '.join(f'{k}={v!r}' for k, v in args.items())})")
    for name, resp in result["results"]:
        print(f"  \U0001F4E6 {name} -> {resp}")
    print(f"  \U0001F4AC {result['reply'].strip()}")


async def main(which: list[int]) -> None:
    from broken_agent.agent import root_agent as broken
    from fixed_agent.agent import root_agent as fixed

    for n in which:
        title, messages = DEMOS[n]
        print(f"\n=== Problem {n}: {title} ===")
        print(f"  \U0001F464 {messages[0]}")
        if n == 3:
            payments.DOWN_FLAG.write_text("down for rehearsal\n")
        try:
            show("BROKEN", await run_once(broken, messages))
            show("FIXED", await run_once(fixed, messages))
        finally:
            if n == 3:
                payments.DOWN_FLAG.unlink(missing_ok=True)


if __name__ == "__main__":
    if not has_api_key():
        sys.exit("No API key. Copy .env.example to .env and add your GOOGLE_API_KEY first.")
    picked = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4]
    asyncio.run(main(picked))
