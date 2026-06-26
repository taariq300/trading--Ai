import pandas as pd


def run_backtest(df: pd.DataFrame, signal_col: str = "signal", initial_cash: float = 10000) -> pd.DataFrame:
    """
    df must have a 'Close' column and a signal column (1 = hold long, 0 = flat).
    Returns df with added columns: position, market_returns, strategy_returns,
    equity, benchmark_equity.

    Note: position is the PREVIOUS bar's signal (shift by 1). This avoids
    look-ahead bias - you can only act on a signal after it appears, not
    on the same bar it was generated.
    """
    df = df.copy()
    df["position"] = df[signal_col].shift(1).fillna(0)
    df["market_returns"] = df["Close"].pct_change()
    df["strategy_returns"] = df["position"] * df["market_returns"]

    df["equity"] = initial_cash * (1 + df["strategy_returns"].fillna(0)).cumprod()
    df["benchmark_equity"] = initial_cash * (1 + df["market_returns"].fillna(0)).cumprod()

    return df
