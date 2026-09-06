# Signal

A market watchlist that tells you what actually changed since you last looked, instead of making you scan every stock yourself.

A normal watchlist is a lookup tool where you open it and read the prices. That's fine if you're staring at it all day, but most people aren't. They track 20 or 40 stocks and check in a few times a week, and the real question isn't "what's the price," it's "which of these did something worth my attention, and why." Signal tries to answer that second question.

## What it does

You build a watchlist, go away, come back later. Instead of a wall of numbers, the first thing you see is a short list of the stocks that did something unusual since your last visit, each with a plain-language reason. The full watchlist is still there in a separate tab if you want to browse everything, quiet stocks included. When nothing's going on, it just says so.

## How it decides what's "meaningful"

"Meaningful" here means *unusual for that particular stock*, not big in absolute terms. A 5% move is nothing for a stock that swings 5% every week, and a 1.5% move is a lot for one that never moves. So every signal is measured against the stock's own recent behavior, not a fixed threshold.

Three signals feed into it:

- **Price move** — today's move compared to how much this stock normally moves day to day.
- **Volume** — today's volume compared to its own recent average.
- **Index-relative move** — the move after you subtract what the whole market did. If the S&P dropped 3% and so did your stock, that's not news about your stock. If your stock dropped 3% on a flat market, that is.

They don't fire independently. A single signal is treated as noise — a stock only gets flagged when at least two of the three line up on the same day. Two is a medium-confidence flag, three is high. That's the main thing keeping the feed quiet; it's deliberately hard to trip.

Every flag stores its reasons as actual data, not just a score, so the app can always say *why* a stock is in your feed. A number with no explanation is a black box, and that was a rule from the start.

The lookback window is capped at 30 days regardless of how long you've been gone. If you haven't opened the app in six months, comparing today against a six-month-old baseline doesn't tell you anything real — a stock can drift 40% over that time with nothing actually happening. So the "unusual" check always runs over a recent window. The "up 22% since you last checked" line is shown separately, as plain context, and is never treated as a signal on its own.

## Running it locally

You'll need Python 3.10+ and Node 18+.

### Backend

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Get a free API key from [twelvedata.com](https://twelvedata.com) and put it in a `.env` file inside `backend/`:

```
TWELVEDATA_API_KEY=your_key_here
```

Then create the database and start the server:

```
python create_tables.py
uvicorn app.main:app --reload
```

Runs on http://localhost:8000.

### Frontend

In a second terminal:

```
cd frontend
npm install
npm run dev
```

Runs on http://localhost:5173 (or the next free port if that's taken). It talks to the backend at localhost:8000 by default; set `VITE_API_URL` if yours is elsewhere.

### Getting some data to look at

A brand-new account is empty and says "All quiet," which is correct but boring to demo. Real flags only show up when the market actually does something unusual, so there's a seed script to skip the wait:

```
cd backend
python seed_demo.py your@email.com
```

## How it's put together

React frontend, FastAPI backend, SQLite in between.

The backend is split so the one messy part — talking to the market data API — is isolated. A fetcher pulls daily price bars and stores them. A separate engine reads those stored bars and works out which stocks are meaningful, writing out flags with their reasons. The API layer just serves what's already been computed. A background job refreshes the data once a day after market close.

The point of that split: the meaningfulness logic never touches the outside world, so it's easy to test on its own — feed it fake numbers, check which signals fire — and the app keeps working off stored data even if the market API is down when you open it.

## Some decisions and why

**SQLite, not Postgres.** This is a single-node app with a tiny amount of data. SQLite means there's no database server to configure or fall over during a demo. It runs in WAL mode so the daily job can write while the app reads. The one real limit is concurrent writers, and that doesn't bite here since the only writer is that one daily job. Moving to Postgres later is basically a connection-string change — building for that now would be solving a problem I don't have yet.

**One data source.** The brief mentions handling conflicting data from multiple sources. I thought about it and decided one authoritative source is the honest call, rather than building a reconciliation system for a conflict I'd be inventing. The fetcher is isolated, so swapping providers later is a one-file change. If I did add a second source, I'd flag disagreement rather than silently average the two.

**Daily data, polled once a day, not real-time.** The signals are all computed over daily bars, so second-by-second data would add noise and burn rate limits for no benefit. Free-tier data is delayed anyway, and pretending otherwise would be dishonest.

**A hand-written rules engine, not machine learning.** I can explain exactly why any flag fired, I can unit-test it, and I could actually build it in the time I had.

**Minimal auth.** Real email/password login with hashed passwords and a token, because "what changed since *you* last looked" needs real accounts. But no OAuth, no password reset, no refresh tokens — enough to keep state per user and nothing more.

**One "last seen" cursor per user.** A single timestamp drives what counts as new. Reading the feed doesn't move it — otherwise refreshing the page would clear your feed instantly. It moves only when you click "Mark as reviewed." So the model is "since you last reviewed," and there's no per-stock read/unread state anywhere.


## Tests

```
cd backend
pytest
```

The signal math and the engine's combination logic are covered against hand-made inputs, plus the auth, watchlist, and feed endpoints against a throwaway database.