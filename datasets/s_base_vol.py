import pandas as pd

def analyze_volume(file_path, prev_days=20, next_days=14):
    df = pd.read_csv(
        file_path,
        parse_dates=["Date"],
        index_col="Date"
    )

    df = df.sort_index()
    df = df.loc[~df.index.duplicated(keep="first")]

    # Adjust Open to the same scale as Adj Close.
    adj_factor = df["Adj Close"] / df["Close"]
    adj_open = df["Open"] * adj_factor
    adj_close = df["Adj Close"]

    # Today's volume relative to the average of the previous x sessions.
    previous_xd_avg_volume = df["Volume"].shift(1).rolling(prev_days).mean()
    df["volume_ratio"] = df["Volume"] / previous_xd_avg_volume

    # Return from next session's Open to the y session's Close.
    df["forward_return"] = adj_close.shift(-next_days) / adj_open.shift(-1) - 1

    df = df.dropna(subset=["volume_ratio", "forward_return"])

    # Pre-set ranges: 0.8 means 20% below average; 1.5 means 50% above.
    df["volume_group"] = pd.cut(
        df["volume_ratio"],
        bins=[0, 0.8, 1.2, 1.5, float("inf")],
        labels=["< 0.8× average", "0.8–1.2×", "1.2–1.5×", "> 1.5×"],
        include_lowest=True
    )

    # Keep the latest 20% as a holdout test.
    test = df.iloc[int(len(df) * 0.8):]

    summary = test.groupby("volume_group", observed=True)["forward_return"].agg(
        count="count",
        win_rate=lambda returns: (returns > 0).mean(),
        average_return="mean",
        median_return="median"
    )

    print("Average return across all test dates:",
          f"{test['forward_return'].mean():.2%}")
    print(summary.to_string())
    return

