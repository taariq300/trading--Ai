# Trading AI — Strategy Backtester (Streamlit Dashboard)

A web dashboard for backtesting simple technical-indicator trading strategies
against historical price data. Built as a research/learning tool — see the
caveats at the bottom before using it for anything real.

## What it does

- Pick any stock ticker and date range
- Choose a strategy: **Moving Average Crossover** or **RSI Mean-Reversion**
- Tune the strategy's parameters with sliders
- See an equity curve vs. buy-and-hold, a price chart with buy/sell markers,
  and performance metrics (return, drawdown, Sharpe ratio, trade count)

## Project structure

```
trading-ai-app/
  app.py              # Streamlit app (run this)
  data.py              # fetches price data via yfinance
  indicators.py        # moving averages, RSI
  strategy.py          # turns indicators into buy/sell signals
  backtest.py          # simulates the strategy over history
  metrics.py            # performance stats
  requirements.txt      # dependencies for deployment
```

## Run it locally first (recommended before deploying)

1. Install [Python 3.10+](https://www.python.org/downloads/) if you don't have it.
2. In this folder, install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. It opens automatically at `http://localhost:8501`. Try a ticker like `AAPL`
   or `MSFT`, click **Run Backtest**, and confirm it works before deploying.

## Deploy it as an always-available web app (free)

This uses **GitHub** (to host the code) + **Streamlit Community Cloud**
(to host the running app).

### 1. Push this folder to GitHub

- Create a new repository at [github.com/new](https://github.com/new)
  (can be public or private).
- Upload all the files in this folder to that repo (drag-and-drop on the
  GitHub website works fine, or use `git push` if you're comfortable with git).

### 2. Deploy on Streamlit Community Cloud

- Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
  your GitHub account.
- Click **"New app"**.
- Select your repository, the branch (usually `main`), and set the
  **main file path** to `app.py`.
- Click **Deploy**.

That's it — Streamlit installs everything from `requirements.txt` automatically
and gives you a public URL (something like `yourname-trading-ai.streamlit.app`)
that's live and reachable anytime, from any device.

### 3. Updating it later

Any time you push new changes to the GitHub repo, Streamlit Cloud
automatically redeploys the app with the update. No manual redeploy step.

## Extending it

The code is split into independent modules on purpose:

- Add a new strategy → write a new function in `strategy.py` that takes a
  DataFrame and returns a `signal` column, then add it to the dropdown in `app.py`.
- Swap in a machine learning model later → same interface: a function that
  outputs a `signal` column. The backtest engine doesn't need to change.

## Important caveats

- **Not financial advice.** This is a tool for testing ideas, not a system
  for generating real trading decisions.
- **Backtests overstate real-world performance.** This version ignores
  trading fees, slippage, and taxes, and assumes you can buy/sell at the
  exact closing price.
- **A good-looking backtest is not evidence of a real edge.** It's easy to
  pick parameters that happen to work well on one historical period
  (overfitting). Try the same strategy on a different ticker or date range
  before trusting the result.
- **No live or real-money trading is connected here.** This dashboard only
  simulates trades against historical data.
