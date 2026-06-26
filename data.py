import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache_data(show_spinner=False)
def get_price_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetch daily OHLCV data for a ticker between start and end dates.
    Dates as 'YYYY-MM-DD' strings (or datetime.date objects).
    Cached so repeated requests with the same args don't re-hit the network.
    """
    df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

    if df is None or df.empty:
        return pd.DataFrame()

    # yfinance sometimes returns multi-index columns (e.g. for multiple tickers) - flatten if so
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]

    df = df.dropna()
    return df
