import numpy as np
import pandas as pd


def compute_metrics(df: pd.DataFrame) -> dict:
    total_return = df["equity"].iloc[-1] / df["equity"].iloc[0] - 1
    benchmark_return = df["benchmark_equity"].iloc[-1] / df["benchmark_equity"].iloc[0] - 1

    running_max = df["equity"].cummax()
    drawdown = (df["equity"] - running_max) / running_max
    max_drawdown = drawdown.min()

    daily_ret = df["strategy_returns"].dropna()
    sharpe = (daily_ret.mean() / daily_ret.std()) * np.sqrt(252) if daily_ret.std() not in (0, None) and not pd.isna(daily_ret.std()) else float("nan")

    trades = df["position"].diff().fillna(0)
    num_trades = int((trades != 0).sum())

    return {
        "Total Return": f"{total_return * 100:.2f}%",
        "Buy & Hold Return": f"{benchmark_return * 100:.2f}%",
        "Max Drawdown": f"{max_drawdown * 100:.2f}%",
        "Sharpe Ratio": f"{sharpe:.2f}" if not pd.isna(sharpe) else "N/A",
        "Number of Trades": num_trades,
    }
