import pandas as pd

def tend_rise(file_path,short_av=20,long_av=50, d_mom=20):
    df = pd.read_csv(
        file_path,
        parse_dates=["Date"],
        index_col="Date"
    )

    df = df.sort_index()
    df = df.loc[~df.index.duplicated(keep="first")]

    # Adjust Open to the same scale as Adj Close.
    factor = df["Adj Close"] / df["Close"]
    adj_close = df["Adj Close"]
    adj_open = df["Open"] * factor

    df["maShort"] = adj_close.rolling(short_av).mean()
    df["maLong"] = adj_close.rolling(long_av).mean()
    df["momD"] = adj_close / adj_close.shift(d_mom) - 1

    # Signal is based only on information available at that day's close.
    df["signal"] = (
        (adj_close > df["maShort"]) &
        (df["maShort"] > df["maLong"]) &
        (df["momD"] > 0)
    )

    # Approximate trade: enter at the next session's adjusted Open,
    # exit at the adjusted Close five trading sessions after entry.
    df["fwd_5d_return"] = adj_close.shift(-5) / adj_open.shift(-1) - 1
    df = df.dropna()

    # Reserve the latest 20% of dates for testing.
    cut = int(len(df) * 0.8)
    test = df.iloc[cut:]
    signals = test[test["signal"]]

    print("Test dates:", test.index.min(), "to", test.index.max())
    print("Number of signals:", len(signals))

    if len(signals):
        print("Signal win rate:", (signals["fwd_5d_return"] > 0).mean())
        print("Signal average return:", signals["fwd_5d_return"].mean())

    print("Average return across all test dates:", test["fwd_5d_return"].mean())
    print()

    return 
