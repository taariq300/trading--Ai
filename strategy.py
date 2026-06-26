import pandas as pd


def ma_crossover_strategy(df: pd.DataFrame) -> pd.DataFrame:
    """Requires ma_short and ma_long columns already present."""
    df = df.copy()
    df["signal"] = (df["ma_short"] > df["ma_long"]).astype(int)
    return df


def rsi_strategy(df: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> pd.DataFrame:
    """
    Requires rsi column already present.
    Stateful long/flat logic: buy when RSI drops below 'oversold',
    sell/flat when RSI rises above 'overbought', otherwise hold position.
    """
    df = df.copy()
    signal = []
    holding = 0
    for rsi_val in df["rsi"]:
        if pd.isna(rsi_val):
            signal.append(0)
            continue
        if rsi_val < oversold:
            holding = 1
        elif rsi_val > overbought:
            holding = 0
        signal.append(holding)
    df["signal"] = signal
    return df
