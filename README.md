# Break It, Fix It

**"You built an agent. Now let's break it."** Talk materials for final-year students at a Google Developer Community event, by Umashankar P.

Building an AI agent takes an afternoon. Making it trustworthy is the actual job. This repo shows **four real ways agents fail**, with a working broken agent, a working fixed agent, and a detailed write-up of each problem and its solution.

## The problems and solutions

| # | Problem | What goes wrong | The fix | Write-up |
|---|---|---|---|---|
| 1 | **It makes things up** | Asked about returns, it invents a "30-day refund" policy. | A source of truth (`get_policy`) and permission to say "I don't know". | [📖 Read](problems/01-makes-things-up/README.md) |
| 2 | **It picks the wrong tool** | "Cancel my order" becomes a refund; the shoes still ship. | The right tool, clear descriptions, inputs checked in code. | [📖 Read](problems/02-wrong-tool/README.md) |
| 3 | **It fails silently** | The payment gateway times out, and it says "refund processed". | Loud errors, success only with proof, limited retries. | [📖 Read](problems/03-silent-failure/README.md) |
| 4 | **A review takes control** | A product review tells the agent to apply a 100% coupon (prompt injection). | Rules in code, human approval, untrusted-data labels, minimum access. | [📖 Read](problems/04-prompt-injection/README.md) |
| ★ | **Student challenge** | Get ₹4,999 headphones as cheaply as possible. | Spoilers inside. | [📖 Read](problems/05-student-challenge/README.md) |

Start with the [overview of all problems](problems/README.md).

> **Rules in the prompt are suggestions. Rules in the code are laws.**

## What's in the repo

| Path | What it is |
|---|---|
| [`problems/`](problems/README.md) | One detailed README per problem: the demo, a real run, why it happens, before/after code, how to try it, and the tests. |
| [`break-it-fix-it.html`](break-it-fix-it.html) | The presentation. Download it, open it in Chrome and press `F`; `→` steps through, `N` jumps to the next problem. |
| [`shopbuddy/`](shopbuddy/README.md) | **ShopBuddy**, an online-store support agent (Google ADK + Gemini): `broken_agent/`, `fixed_agent/`, `challenge_agent/` + student chat page, rehearsal and attack scripts, tests. |
| [`START-HERE.md`](START-HERE.md) | Presenter guide: setup, checklist, run-of-show, demo script, troubleshooting. |
| [`CLAUDE.md`](CLAUDE.md) | Project context for Claude Code. |

## Quick start

```bash
git clone https://github.com/upardhi/break-it-fix-it.git
cd break-it-fix-it/shopbuddy
python -m venv .venv
.venv\Scripts\activate             # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env             # Mac/Linux: cp .env.example .env
```

Put your Gemini API key (from https://aistudio.google.com/apikey) in `shopbuddy/.env`, then:

```bash
python -m pytest tests/test_tools.py   # 19 offline tests, no API key needed
python rehearse.py                     # all 4 problems on the broken and fixed agents
adk web                                # interactive UI at http://localhost:8000
```

Windows tip: clone to a short path such as `C:\talk`. Very long paths can break `pip install`.
