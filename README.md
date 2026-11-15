# Break It, Fix It

Talk materials for **"You built an agent. Now let's break it."**, a session for final-year students at a Google Developer Community event, by Umashankar P.

- **`break-it-fix-it.html`**: the presentation. Download it, open it in Chrome and press `F` for fullscreen; `→` steps through, `N` jumps to the next problem.
- **`shopbuddy/`**: ShopBuddy, an online-store support agent built with Google ADK and Gemini, in a **broken** and a **fixed** version. It covers four ways agents fail:
  1. making things up
  2. picking the wrong tool
  3. failing silently
  4. obeying instructions hidden in a product review (prompt injection)

  It also includes a breakable agent for a live student challenge, with a chat page and a leaderboard.

**Start with [START-HERE.md](START-HERE.md)** for setup, the demo script and the run-of-show.

You'll need your own Gemini API key from https://aistudio.google.com/apikey: copy `shopbuddy/.env.example` to `shopbuddy/.env` and paste it in.
