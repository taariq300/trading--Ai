import datetime as dt

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from backtest import run_backtest
from data import get_price_data
from indicators import add_moving_averages, add_rsi
from metrics import compute_metrics
from strategy import ma_crossover_strategy, rsi_strategy

st.set_page_config(page_title="Trading AI Backtester", layout="wide")

st.title("📈 Trading AI — Strategy Backtester")
st.caption(
    "A research and learning tool for testing trading rules against history. "
    "Not financial advice, and a good backtest is not proof of a real edge."
)

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.header("Settings")

    ticker = st.text_input("Ticker", value="AAPL").upper().strip()

    today = dt.date.today()
    default_start = today - dt.timedelta(days=365 * 3)
    start_date = st.date_input("Start date", value=default_start, max_value=today)
    end_date = st.date_input("End date", value=today, max_value=today)

    initial_cash = st.number_input("Initial cash ($)", value=10000, min_value=100, step=500)

    st.divider()
    strategy_choice = st.selectbox(
        "Strategy",
        ["Moving Average Crossover", "RSI Mean-Reversion"],
    )

    if strategy_choice == "Moving Average Crossover":
        short_window = st.slider("Short MA window (days)", 5, 100, 20)
        long_window = st.slider("Long MA window (days)", 10, 250, 50)
    else:
        rsi_period = st.slider("RSI period (days)", 5, 50, 14)
        oversold = st.slider("Oversold threshold (buy below)", 5, 45, 30)
        overbought = st.slider("Overbought threshold (sell above)", 55, 95, 70)

    run_clicked = st.button("Run Backtest", type="primary", use_container_width=True)
    if run_clicked:
        st.session_state["has_run"] = True

# ---------------- Main logic ----------------
if st.session_state.get("has_run"):
    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    with st.spinner(f"Fetching data for {ticker}..."):
        raw_df = get_price_data(ticker, str(start_date), str(end_date))

    if raw_df.empty:
        st.error(
            f"No data found for '{ticker}'. Check the ticker symbol and date range, "
            "then try again."
        )
        st.stop()

    # Apply indicators + strategy
    if strategy_choice == "Moving Average Crossover":
        df = add_moving_averages(raw_df, short_window, long_window)
        df = ma_crossover_strategy(df)
        strategy_label = f"MA Crossover ({short_window}/{long_window})"
    else:
        df = add_rsi(raw_df, rsi_period)
        df = rsi_strategy(df, oversold, overbought)
        strategy_label = f"RSI Mean-Reversion ({rsi_period}, {oversold}/{overbought})"

    result = run_backtest(df, initial_cash=initial_cash)
    metrics = compute_metrics(result)

    # ---------------- Metrics row ----------------
    st.subheader(f"Results: {ticker} — {strategy_label}")
    cols = st.columns(len(metrics))
    for col, (label, value) in zip(cols, metrics.items()):
        col.metric(label, value)

    strat_better = float(metrics["Total Return"].rstrip("%")) > float(
        metrics["Buy & Hold Return"].rstrip("%")
    )
    if strat_better:
        st.success("This strategy outperformed buy-and-hold over this exact period.")
    else:
        st.info("Buy-and-hold outperformed this strategy over this exact period.")

    # ---------------- Equity curve chart ----------------
    st.subheader("Equity Curve")
    fig_equity = go.Figure()
    fig_equity.add_trace(
        go.Scatter(x=result.index, y=result["equity"], name="Strategy", line=dict(color="#1F77B4"))
    )
    fig_equity.add_trace(
        go.Scatter(
            x=result.index,
            y=result["benchmark_equity"],
            name="Buy & Hold",
            line=dict(color="#999999", dash="dash"),
        )
    )
    fig_equity.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Portfolio Value ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_equity, use_container_width=True)

    # ---------------- Price chart with signals ----------------
    st.subheader("Price & Signal")
    fig_price = go.Figure()
    fig_price.add_trace(
        go.Scatter(x=result.index, y=result["Close"], name="Close", line=dict(color="#333333"))
    )

    if strategy_choice == "Moving Average Crossover":
        fig_price.add_trace(
            go.Scatter(x=result.index, y=result["ma_short"], name=f"MA {short_window}", line=dict(color="#2CA02C"))
        )
        fig_price.add_trace(
            go.Scatter(x=result.index, y=result["ma_long"], name=f"MA {long_window}", line=dict(color="#D62728"))
        )
    else:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=result.index, y=result["rsi"], name="RSI", line=dict(color="#9467BD")))
        fig_rsi.add_hline(y=overbought, line_dash="dot", line_color="red")
        fig_rsi.add_hline(y=oversold, line_dash="dot", line_color="green")
        fig_rsi.update_layout(height=220, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="RSI")

    # mark entries/exits
    entries = result[result["position"].diff() == 1]
    exits = result[result["position"].diff() == -1]
    fig_price.add_trace(
        go.Scatter(
            x=entries.index, y=entries["Close"], mode="markers", name="Buy",
            marker=dict(symbol="triangle-up", color="green", size=10),
        )
    )
    fig_price.add_trace(
        go.Scatter(
            x=exits.index, y=exits["Close"], mode="markers", name="Sell",
            marker=dict(symbol="triangle-down", color="red", size=10),
        )
    )
    fig_price.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Price ($)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_price, use_container_width=True)

    if strategy_choice == "RSI Mean-Reversion":
        st.plotly_chart(fig_rsi, use_container_width=True)

    # ---------------- Trade log ----------------
    with st.expander("Trade log (raw data)"):
        display_cols = ["Close", "position", "strategy_returns", "equity", "benchmark_equity"]
        st.dataframe(result[display_cols].tail(200), use_container_width=True)

else:
    st.info("Set your parameters in the sidebar and click **Run Backtest** to get started.")

st.divider()
st.caption(
    "⚠️ This tool is for research and education. No strategy shown here is a recommendation "
    "to buy or sell anything. Past performance in a backtest does not predict future results, "
    "and these backtests do not account for trading fees, slippage, or taxes."
)
