from pathlib import Path

import numpy as np
import pandas as pd

RULES = ["trend", "breakout", "mean_reversion"]

def _load_data(path):
    df = pd.read_csv(path)

    if "Date" not in df.columns:
        raise ValueError(f"{path}: no 'Date' column; columns are {list(df.columns)}")

    dates = pd.to_datetime(
        df.pop("Date"),
        format="mixed",
        errors="coerce",
        utc=True,
    )

    if dates.isna().any():
        bad_rows = dates[dates.isna()].index[:5].tolist()
        raise ValueError(f"{path}: unparseable dates at rows {bad_rows}")

    dates = dates.dt.tz_convert("Australia/Sydney").dt.tz_localize(None)
    df.index = pd.DatetimeIndex(dates, name="Date")
    df = df.sort_index()

    df = df.loc[~df.index.duplicated(keep="first")].copy()

    required = {"Open", "Close", "Adj Close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{path}: missing columns {sorted(missing)}")

    adj_close = df["Adj Close"].astype(float)
    adj_open = df["Open"].astype(float) * (
        adj_close / df["Close"].astype(float)
    )

    df["adj_close"] = adj_close
    df["adj_open"] = adj_open

    # Indicators use data available by that day's close.
    df["ma20"] = adj_close.rolling(20).mean()
    df["ma50"] = adj_close.rolling(50).mean()
    df["mom20"] = adj_close / adj_close.shift(20) - 1
    df["prior_high20"] = adj_close.shift(1).rolling(20).max()

    change = adj_close.diff()
    avg_gain = change.clip(lower=0).rolling(14).mean()
    avg_loss = -change.clip(upper=0).rolling(14).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi14"] = 100 - (100 / (1 + rs))
    df.loc[(avg_loss == 0) & (avg_gain > 0), "rsi14"] = 100

    mid = adj_close.rolling(20).mean()
    sd = adj_close.rolling(20).std(ddof=0)
    df["bb_lower"] = mid - 2 * sd

    df["trend"] = (
        (adj_close > df["ma20"])
        & (df["ma20"] > df["ma50"])
        & (df["mom20"] > 0)
    )
    df["breakout"] = adj_close > df["prior_high20"]
    df["mean_reversion"] = (
        (adj_close < df["bb_lower"])
        & (df["rsi14"] < 30)
    )

    # Signal on day t close; enter at t+1 open; exit at t+5 close.
    df["forward_return"] = (
        adj_close.shift(-5) / adj_open.shift(-1) - 1
    )

    for rule in RULES:
        df[rule] = df[rule].fillna(False).astype(bool)

    return df


def _wilson_interval(wins, n, z=1.96):
    if n == 0:
        return np.nan, np.nan

    p = wins / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt(
        p * (1 - p) / n + z**2 / (4 * n**2)
    ) / denom
    return center - half, center + half


def _metrics(returns):
    r = np.asarray(returns, dtype=float)
    r = r[np.isfinite(r)]

    if len(r) == 0:
        return {
            "trades": 0,
            "win_rate_%": np.nan,
            "win_rate_95%_CI": "",
            "avg_win_%": np.nan,
            "avg_loss_%": np.nan,
            "expectancy_%": np.nan,
            "profit_factor": np.nan,
            "compound_return_%": np.nan,
            "trade_curve_max_DD_%": np.nan,
        }

    wins = r[r > 0]
    losses = r[r < 0]
    lo, hi = _wilson_interval(len(wins), len(r))

    equity = np.r_[1.0, np.cumprod(1 + r)]
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1

    if len(losses):
        profit_factor = wins.sum() / abs(losses.sum())
    elif len(wins):
        profit_factor = np.inf
    else:
        profit_factor = np.nan

    return {
        "trades": len(r),
        "win_rate_%": 100 * (r > 0).mean(),
        "win_rate_95%_CI": f"{100 * lo:.1f}–{100 * hi:.1f}%",
        "avg_win_%": 100 * wins.mean() if len(wins) else np.nan,
        "avg_loss_%": 100 * losses.mean() if len(losses) else np.nan,
        "expectancy_%": 100 * r.mean(),
        "profit_factor": profit_factor,
        "compound_return_%": 100 * (equity[-1] - 1),
        "trade_curve_max_DD_%": 100 * drawdown.min(),
    }


def _compare_one_file(
    path,
    cost_bps=10,
    initial_train=3 * 252,
    test_size=252,
):
    df = _load_data(path)
    if len(df) <= initial_train:
        raise ValueError(
            f"{path}: needs more than {initial_train} rows; has {len(df)}"
        )

    cost = cost_bps / 10_000
    all_returns = {rule: [] for rule in RULES}
    all_returns["buy_and_hold"] = []
    fold_rows = []

    for start in range(initial_train, len(df), test_size):
        end = min(start + test_size, len(df))
        period = f"{df.index[start].date()} to {df.index[end - 1].date()}"

        for rule in RULES:
            returns = []
            last_exit = -1

            for i in range(start, end):
                # Keep each trade's exit within its test fold.
                if i + 5 >= end or i < last_exit:
                    continue
                if not df[rule].iloc[i]:
                    continue

                gross_return = df["forward_return"].iloc[i]
                if not np.isfinite(gross_return):
                    continue

                returns.append(gross_return - cost)
                last_exit = i + 5

            all_returns[rule].extend(returns)
            fold_rows.append({
                "test_period": period,
                "rule": rule,
                **_metrics(returns),
            })

        # One buy-and-hold return for the same test period.
        bh_return = (
            df["adj_close"].iloc[end - 1] / df["adj_close"].iloc[start]
            - 1 - cost
        )
        all_returns["buy_and_hold"].append(bh_return)
        fold_rows.append({
            "test_period": period,
            "rule": "buy_and_hold",
            **_metrics([bh_return]),
        })

    summary_rows = [
        {"rule": rule, **_metrics(returns)}
        for rule, returns in all_returns.items()
    ]

    folds = pd.DataFrame(fold_rows)
    summary = pd.DataFrame(summary_rows)

    # Keep the source file on every row so results can be combined.
    file_name = Path(path).name
    folds.insert(0, "file", file_name)
    summary.insert(0, "file", file_name)

    return summary, folds


def compare_csv_files(
    paths,
    cost_bps=10,
    initial_train=3 * 252,
    test_size=252,
):
    """
    Compare the fixed rules across one or more CSV files.

    Returns:
        summary: one combined out-of-sample row per file and rule
        folds:   one row per file, test period, and rule
    """
    if isinstance(paths, (str, Path)):
        paths = [paths]

    summaries = []
    fold_results = []

    for path in paths:
        summary, folds = _compare_one_file(
            path=path,
            cost_bps=cost_bps,
            initial_train=initial_train,
            test_size=test_size,
        )
        summaries.append(summary)
        fold_results.append(folds)

    return (
        pd.concat(summaries, ignore_index=True),
        pd.concat(fold_results, ignore_index=True),
    )
