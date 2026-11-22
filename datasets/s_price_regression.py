from pathlib import Path

import pandas as pd

import numpy as np

def find_triangle_breakout_followups(
    csv_files,
    pattern_records=20,
    lookahead_records=15,
    min_contraction=0.70,
    breakout_buffer=0.0,
    flat_slope_pct=0.01,
):
    """
    Find bullish triangle breakouts and return following rows whose Close
    is higher than the breakout row's Close.

    A triangle is approximated by converging regression lines fitted to
    High and Low over the preceding `pattern_records` rows.

    breakout_buffer=0.0 means Close must be strictly above resistance.
    Set, for example, to 0.002 for a 0.2% breakout margin.
    """
    results = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)

        required = ["Date", "High", "Low", "Close"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"{csv_file}: missing required columns {missing}")

        df["Date"] = pd.to_datetime(df["Date"], utc=True, errors="coerce")
        for col in ["High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = (
            df.dropna(subset=["Date", "High", "Low", "Close"])
              .sort_values("Date")
              .reset_index(drop=True)
        )

        if len(df) <= pattern_records:
            continue

        for i in range(pattern_records, len(df)):
            history = df.iloc[i - pattern_records:i]
            x = np.arange(pattern_records, dtype=float)

            # Fit the upper and lower triangle boundaries from prior records.
            upper_slope, upper_intercept = np.polyfit(
                x, history["High"].to_numpy(), 1
            )
            lower_slope, lower_intercept = np.polyfit(
                x, history["Low"].to_numpy(), 1
            )

            upper_line = upper_slope * x + upper_intercept
            lower_line = lower_slope * x + lower_intercept
            widths = upper_line - lower_line

            # Require a positive, narrowing range.
            if np.any(widths <= 0):
                continue
            if widths[-1] > widths[0] * min_contraction:
                continue

            typical_price = history["Close"].median()
            if not np.isfinite(typical_price) or typical_price <= 0:
                continue

            # Classify the converging triangle using total line movement.
            upper_change = upper_slope * (pattern_records - 1)
            lower_change = lower_slope * (pattern_records - 1)
            flat_limit = typical_price * flat_slope_pct

            upper_flat = abs(upper_change) <= flat_limit
            lower_flat = abs(lower_change) <= flat_limit

            if upper_flat and lower_slope > 0:
                triangle_type = "ascending"
            elif lower_flat and upper_slope < 0:
                triangle_type = "descending"
            elif upper_slope < 0 and lower_slope > 0:
                triangle_type = "symmetrical"
            else:
                continue

            # Project resistance to the current row. The current row is not
            # included in the regression used to construct the triangle.
            prior_resistance = upper_slope * (pattern_records - 1) + upper_intercept
            current_resistance = upper_slope * pattern_records + upper_intercept

            previous_close = df.iloc[i - 1]["Close"]
            signal_close = df.iloc[i]["Close"]

            crossed_above = (
                previous_close <= prior_resistance * (1 + breakout_buffer)
                and signal_close > current_resistance * (1 + breakout_buffer)
            )
            if not crossed_above:
                continue

            # Inspect only the next N records; return those closing above signal.
            end = min(i + 1 + lookahead_records, len(df))
            future = df.iloc[i + 1:end]
            higher_rows = future[future["Close"] > signal_close].copy()

            for future_index, row in higher_rows.iterrows():
                result = row.to_dict()
                result.update({
                    "source_file": Path(csv_file).name,
                    "signal_date": df.iloc[i]["Date"],
                    "signal_close": signal_close,
                    "pct_change": round(
                        ((row["Close"] - signal_close) / signal_close) * 100, 2
                    ),
                    "triangle_type": triangle_type,
                    "records_after_signal": future_index - i,
                })
                results.append(result)


    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_shooting_star_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    min_upper_wick_to_body=2.0,
    max_lower_wick_to_body=1.0,
    max_body_to_range=0.30,
):
    """
    Detect single-candle Shooting Stars, then return follow-up rows whose
    Close is above the Shooting Star candle's Close.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if min_upper_wick_to_body < 0 or max_lower_wick_to_body < 0:
        raise ValueError("Wick-to-body ratios cannot be negative")
    if not 0 <= max_body_to_range <= 1:
        raise ValueError("max_body_to_range must be between 0 and 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, high_col, low_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        for source_col, helper_col in (
            (open_col, "_open"),
            (high_col, "_high"),
            (low_col, "_low"),
            (close_col, "_close"),
        ):
            df[helper_col] = pd.to_numeric(df[source_col], errors="coerce")

        df = (
            df.dropna(
                subset=[
                    "_parsed_date", "_open", "_high", "_low", "_close"
                ]
            )
            .sort_values("_parsed_date")
            .drop_duplicates("_parsed_date", keep="last")
            .reset_index(drop=True)
        )

        for star_idx, candle in df.iterrows():
            candle_range = candle["_high"] - candle["_low"]
            body = abs(candle["_close"] - candle["_open"])

            if candle_range <= 0 or body <= 0:
                continue

            upper_wick = candle["_high"] - max(
                candle["_open"], candle["_close"]
            )
            lower_wick = min(candle["_open"], candle["_close"]) - candle["_low"]

            is_shooting_star = (
                upper_wick >= min_upper_wick_to_body * body
                and lower_wick <= max_lower_wick_to_body * body
                and body / candle_range <= max_body_to_range
            )

            if not is_shooting_star:
                continue

            star_close = candle["_close"]
            following = df.iloc[
                star_idx + 1 : star_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > star_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["shooting_star_date"] = candle["_parsed_date"]
                result["shooting_star_close"] = star_close
                result["pct_change"] = round(((row["Close"] - star_close) / star_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_hammer_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    min_lower_wick_to_body=2.0,
    max_upper_wick_to_body=1.0,
    max_body_to_range=0.30,
):
    """
    Detect single-candle hammers, then return follow-up rows whose Close
    is above the hammer candle's Close.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with hammer
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if min_lower_wick_to_body < 0 or max_upper_wick_to_body < 0:
        raise ValueError("Wick-to-body ratios cannot be negative")
    if not 0 <= max_body_to_range <= 1:
        raise ValueError("max_body_to_range must be between 0 and 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, high_col, low_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        for source_col, helper_col in (
            (open_col, "_open"),
            (high_col, "_high"),
            (low_col, "_low"),
            (close_col, "_close"),
        ):
            df[helper_col] = pd.to_numeric(df[source_col], errors="coerce")

        df = (
            df.dropna(
                subset=[
                    "_parsed_date", "_open", "_high", "_low", "_close"
                ]
            )
            .sort_values("_parsed_date")
            .drop_duplicates("_parsed_date", keep="last")
            .reset_index(drop=True)
        )

        for hammer_idx, candle in df.iterrows():
            candle_range = candle["_high"] - candle["_low"]
            body = abs(candle["_close"] - candle["_open"])

            if candle_range <= 0 or body <= 0:
                continue

            lower_wick = min(candle["_open"], candle["_close"]) - candle["_low"]
            upper_wick = candle["_high"] - max(candle["_open"], candle["_close"])

            is_hammer = (
                lower_wick >= min_lower_wick_to_body * body
                and upper_wick <= max_upper_wick_to_body * body
                and body / candle_range <= max_body_to_range
            )

            if not is_hammer:
                continue

            hammer_close = candle["_close"]
            following = df.iloc[
                hammer_idx + 1 : hammer_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > hammer_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["hammer_date"] = candle["_parsed_date"]
                result["hammer_close"] = hammer_close
                result["pct_change"] = round(((row["Close"] - hammer_close) / hammer_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty



def find_doji_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    max_body_to_range=0.05,
):
    """
    Detect single-candle Dojis and return follow-up rows whose Close is
    above the Doji candle's Close.

    A candle qualifies when:
      abs(Close - Open) / (High - Low) <= max_body_to_range

    A zero-range candle qualifies only when Open, High, Low, and Close
    are all equal.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with Doji
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if not 0 <= max_body_to_range <= 1:
        raise ValueError("max_body_to_range must be between 0 and 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, high_col, low_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        for source_col, helper_col in (
            (open_col, "_open"),
            (high_col, "_high"),
            (low_col, "_low"),
            (close_col, "_close"),
        ):
            df[helper_col] = pd.to_numeric(df[source_col], errors="coerce")

        df = (
            df.dropna(
                subset=[
                    "_parsed_date", "_open", "_high", "_low", "_close"
                ]
            )
            .sort_values("_parsed_date")
            .drop_duplicates("_parsed_date", keep="last")
            .reset_index(drop=True)
        )

        for doji_idx, candle in df.iterrows():
            candle_range = candle["_high"] - candle["_low"]
            body_size = abs(candle["_close"] - candle["_open"])

            if candle_range < 0:
                continue
            elif candle_range == 0:
                is_doji = (
                    candle["_open"]
                    == candle["_high"]
                    == candle["_low"]
                    == candle["_close"]
                )
            else:
                is_doji = body_size / candle_range <= max_body_to_range

            if not is_doji:
                continue

            doji_close = candle["_close"]
            following = df.iloc[
                doji_idx + 1 : doji_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > doji_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["doji_date"] = candle["_parsed_date"]
                result["doji_close"] = doji_close
                result["pct_change"] = round(((row["Close"] - doji_close) / doji_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_piercing_line_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    close_col="Close",
):
    """
    Detect a two-candle Piercing Line pattern, then return follow-up rows
    whose Close is above the second candle's Close.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        for pattern_end_idx in range(1, len(df)):
            first = df.iloc[pattern_end_idx - 1]
            second = df.iloc[pattern_end_idx]

            first_is_bearish = first["_close"] < first["_open"]
            second_is_bullish = second["_close"] > second["_open"]
            second_opens_lower = second["_open"] < first["_close"]

            midpoint = (first["_open"] + first["_close"]) / 2
            second_closes_above_midpoint = second["_close"] > midpoint
            second_stays_below_first_open = (
                second["_close"] < first["_open"]
            )

            if not (
                first_is_bearish
                and second_is_bullish
                and second_opens_lower
                and second_closes_above_midpoint
                and second_stays_below_first_open
            ):
                continue

            pattern_close = second["_close"]
            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_start_date"] = first["_parsed_date"]
                result["pattern_end_date"] = second["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_harami_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    close_col="Close",
    max_second_body_ratio=1 / 3,
):
    """
    Detect bullish or bearish two-candle Harami patterns. Then return rows in
    the lookahead window whose Close is above the second candle's Close.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 type and metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if max_second_body_ratio < 0:
        raise ValueError("max_second_body_ratio cannot be negative")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        for pattern_end_idx in range(1, len(df)):
            first = df.iloc[pattern_end_idx - 1]
            second = df.iloc[pattern_end_idx]

            first_body = abs(first["_close"] - first["_open"])
            second_body = abs(second["_close"] - second["_open"])

            if first_body == 0:
                continue

            first_body_low = min(first["_open"], first["_close"])
            first_body_high = max(first["_open"], first["_close"])
            second_body_low = min(second["_open"], second["_close"])
            second_body_high = max(second["_open"], second["_close"])

            second_inside_first = (
                second_body_low >= first_body_low
                and second_body_high <= first_body_high
            )
            second_is_small = (
                second_body <= max_second_body_ratio * first_body
            )

            bullish_harami = (
                first["_close"] < first["_open"]
                and second["_close"] > second["_open"]
                and second_inside_first
                and second_is_small
            )
            bearish_harami = (
                first["_close"] > first["_open"]
                and second["_close"] < second["_open"]
                and second_inside_first
                and second_is_small
            )

            if bullish_harami:
                pattern_type = "bullish_harami"
            elif bearish_harami:
                pattern_type = "bearish_harami"
            else:
                continue

            pattern_close = second["_close"]
            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_type"] = pattern_type
                result["pattern_start_date"] = first["_parsed_date"]
                result["pattern_end_date"] = second["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_engulfing_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    close_col="Close",
):
    """
    Detect bullish or bearish two-candle body-engulfing patterns.

    Bullish: bearish first candle, then bullish candle whose body engulfs it.
    Bearish: bullish first candle, then bearish candle whose body engulfs it.

    For either type, return follow-up rows whose Close is above the engulfing
    candle's Close.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 type and metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        for pattern_end_idx in range(1, len(df)):
            previous = df.iloc[pattern_end_idx - 1]
            current = df.iloc[pattern_end_idx]

            bullish_engulfing = (
                previous["_close"] < previous["_open"]
                and current["_close"] > current["_open"]
                and current["_open"] <= previous["_close"]
                and current["_close"] >= previous["_open"]
            )

            bearish_engulfing = (
                previous["_close"] > previous["_open"]
                and current["_close"] < current["_open"]
                and current["_open"] >= previous["_close"]
                and current["_close"] <= previous["_open"]
            )

            if bullish_engulfing:
                pattern_type = "bullish_engulfing"
            elif bearish_engulfing:
                pattern_type = "bearish_engulfing"
            else:
                continue

            pattern_close = current["_close"]
            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_type"] = pattern_type
                result["pattern_start_date"] = previous["_parsed_date"]
                result["pattern_end_date"] = current["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_three_black_crows_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    max_lower_wick_ratio=0.20,
    min_body_to_range=0.50,
):
    """
    Detect Three Black Crows, then return rows in the lookahead window
    whose Close is above the third crow's Close.

    Pattern criteria:
      - All three candles are bearish.
      - Each candle closes lower than the preceding candle.
      - Candles two and three open within the previous candle's body.
      - Each candle's body is at least `min_body_to_range` of its full range.
      - Each candle's lower wick is at most `max_lower_wick_ratio` of its range.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if not 0 <= max_lower_wick_ratio <= 1:
        raise ValueError("max_lower_wick_ratio must be between 0 and 1")
    if not 0 <= min_body_to_range <= 1:
        raise ValueError("min_body_to_range must be between 0 and 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, high_col, low_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        for source_col, helper_col in (
            (open_col, "_open"),
            (high_col, "_high"),
            (low_col, "_low"),
            (close_col, "_close"),
        ):
            df[helper_col] = pd.to_numeric(df[source_col], errors="coerce")

        df = (
            df.dropna(
                subset=[
                    "_parsed_date", "_open", "_high", "_low", "_close"
                ]
            )
            .sort_values("_parsed_date")
            .drop_duplicates("_parsed_date", keep="last")
            .reset_index(drop=True)
        )

        for start in range(len(df) - 2):
            candles = [df.iloc[start + offset] for offset in range(3)]

            bearish = all(c["_close"] < c["_open"] for c in candles)
            lower_closes = (
                candles[1]["_close"] < candles[0]["_close"]
                and candles[2]["_close"] < candles[1]["_close"]
            )

            opens_within_previous_bodies = True
            for previous, current in zip(candles, candles[1:]):
                body_low = min(previous["_open"], previous["_close"])
                body_high = max(previous["_open"], previous["_close"])
                if not body_low <= current["_open"] <= body_high:
                    opens_within_previous_bodies = False
                    break

            candle_shapes_ok = True
            for candle in candles:
                candle_range = candle["_high"] - candle["_low"]
                body_size = abs(candle["_close"] - candle["_open"])

                if candle_range <= 0:
                    candle_shapes_ok = False
                    break

                body_ratio = body_size / candle_range
                lower_wick = min(candle["_open"], candle["_close"]) - candle["_low"]
                lower_wick_ratio = lower_wick / candle_range

                if (
                    body_ratio < min_body_to_range
                    or lower_wick_ratio > max_lower_wick_ratio
                ):
                    candle_shapes_ok = False
                    break

            if not (
                bearish
                and lower_closes
                and opens_within_previous_bodies
                and candle_shapes_ok
            ):
                continue

            pattern_end_idx = start + 2
            third_crow = df.iloc[pattern_end_idx]
            pattern_close = third_crow["_close"]

            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_start_date"] = candles[0]["_parsed_date"]
                result["pattern_end_date"] = third_crow["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_three_white_soldiers_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    high_col="High",
    low_col="Low",
    close_col="Close",
    max_upper_wick_ratio=0.20,
    min_body_to_range=0.50,
):
    """
    Detect Three White Soldiers, then return rows in the lookahead window
    whose Close is above the third soldier's Close.

    Pattern criteria:
      - All three candles are bullish.
      - Each candle closes higher than the preceding candle.
      - Candles two and three open within the previous candle's body.
      - Each candle's body is at least `min_body_to_range` of its full range.
      - Each candle's upper wick is at most `max_upper_wick_ratio` of its range.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if not 0 <= max_upper_wick_ratio <= 1:
        raise ValueError("max_upper_wick_ratio must be between 0 and 1")
    if not 0 <= min_body_to_range <= 1:
        raise ValueError("min_body_to_range must be between 0 and 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, high_col, low_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        for source_col, helper_col in (
            (open_col, "_open"),
            (high_col, "_high"),
            (low_col, "_low"),
            (close_col, "_close"),
        ):
            df[helper_col] = pd.to_numeric(df[source_col], errors="coerce")

        df = (
            df.dropna(
                subset=[
                    "_parsed_date", "_open", "_high", "_low", "_close"
                ]
            )
            .sort_values("_parsed_date")
            .drop_duplicates("_parsed_date", keep="last")
            .reset_index(drop=True)
        )

        for start in range(len(df) - 2):
            candles = [df.iloc[start + offset] for offset in range(3)]

            bullish = all(c["_close"] > c["_open"] for c in candles)
            higher_closes = (
                candles[1]["_close"] > candles[0]["_close"]
                and candles[2]["_close"] > candles[1]["_close"]
            )

            opens_within_previous_bodies = True
            for previous, current in zip(candles, candles[1:]):
                body_low = min(previous["_open"], previous["_close"])
                body_high = max(previous["_open"], previous["_close"])
                if not body_low <= current["_open"] <= body_high:
                    opens_within_previous_bodies = False
                    break

            candle_shapes_ok = True
            for candle in candles:
                candle_range = candle["_high"] - candle["_low"]
                body_size = abs(candle["_close"] - candle["_open"])

                if candle_range <= 0:
                    candle_shapes_ok = False
                    break

                body_ratio = body_size / candle_range
                upper_wick = candle["_high"] - max(
                    candle["_open"], candle["_close"]
                )
                upper_wick_ratio = upper_wick / candle_range

                if (
                    body_ratio < min_body_to_range
                    or upper_wick_ratio > max_upper_wick_ratio
                ):
                    candle_shapes_ok = False
                    break

            if not (
                bullish
                and higher_closes
                and opens_within_previous_bodies
                and candle_shapes_ok
            ):
                continue

            pattern_end_idx = start + 2
            third_soldier = df.iloc[pattern_end_idx]
            pattern_close = third_soldier["_close"]

            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_start_date"] = candles[0]["_parsed_date"]
                result["pattern_end_date"] = third_soldier["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty



def find_evening_star_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    close_col="Close",
    middle_body_max_ratio=0.30,
    recovery_fraction=0.50,
):
    """
    Detect a three-candle Evening Star pattern, then find rows in the
    lookahead window whose Close is above the pattern's final Close.

    Pattern:
      1. First candle is bullish.
      2. Second candle's body is small relative to the first candle's body.
      3. Third candle is bearish and closes below the specified fraction
         of the first candle's body. By default, this is its midpoint.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if middle_body_max_ratio < 0:
        raise ValueError("middle_body_max_ratio cannot be negative")
    if not 0 < recovery_fraction <= 1:
        raise ValueError("recovery_fraction must be greater than 0 and at most 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        # start is candle 1; start + 1 is candle 2; start + 2 is candle 3.
        for start in range(len(df) - 2):
            first = df.iloc[start]
            second = df.iloc[start + 1]
            third = df.iloc[start + 2]

            first_body = abs(first["_close"] - first["_open"])
            second_body = abs(second["_close"] - second["_open"])

            if first_body == 0:
                continue

            first_is_bullish = first["_close"] > first["_open"]
            middle_is_small = (
                second_body <= middle_body_max_ratio * first_body
            )
            third_is_bearish = third["_close"] < third["_open"]

            # For a bullish first candle, the midpoint is measured up from
            # its open. The third candle must close below that level.
            midpoint_level = (
                first["_open"] + recovery_fraction * first_body
            )
            third_closes_low_enough = third["_close"] < midpoint_level

            if not (
                first_is_bullish
                and middle_is_small
                and third_is_bearish
                and third_closes_low_enough
            ):
                continue

            pattern_end_idx = start + 2
            pattern_close = third["_close"]

            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_start_date"] = first["_parsed_date"]
                result["pattern_end_date"] = third["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty


def find_morning_star_followups(
    paths,
    lookahead_records=15,
    date_col="Date",
    open_col="Open",
    close_col="Close",
    middle_body_max_ratio=0.30,
    recovery_fraction=0.50,
):
    """
    Detect a three-candle Morning Star pattern, then find higher-closing rows
    in the following lookahead window.

    Pattern:
      1. First candle is bearish.
      2. Second candle's body is small relative to the first candle's body.
      3. Third candle is bullish and closes above the specified fraction
         of the first candle's body. By default, this is its midpoint.

    Returns:
        matches: DataFrame of qualifying full follow-up rows, with pattern
                 metadata added.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")
    if middle_body_max_ratio < 0:
        raise ValueError("middle_body_max_ratio cannot be negative")
    if not 0 < recovery_fraction <= 1:
        raise ValueError("recovery_fraction must be greater than 0 and at most 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        # start is candle 1; start + 1 is candle 2; start + 2 is candle 3.
        for start in range(len(df) - 2):
            first = df.iloc[start]
            second = df.iloc[start + 1]
            third = df.iloc[start + 2]

            first_body = abs(first["_open"] - first["_close"])
            second_body = abs(second["_open"] - second["_close"])

            if first_body == 0:
                continue

            first_is_bearish = first["_close"] < first["_open"]
            middle_is_small = (
                second_body <= middle_body_max_ratio * first_body
            )
            third_is_bullish = third["_close"] > third["_open"]

            recovery_level = (
                first["_close"] + recovery_fraction * first_body
            )
            third_closes_high_enough = third["_close"] > recovery_level

            if not (
                first_is_bearish
                and middle_is_small
                and third_is_bullish
                and third_closes_high_enough
            ):
                continue

            pattern_end_idx = start + 2
            pattern_close = third["_close"]

            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]
            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_start_date"] = first["_parsed_date"]
                result["pattern_end_date"] = third["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty

def find_candle_pattern_followups(
    paths,
    date_col="Date",
    open_col="Open",
    close_col="Close",
    lookahead_records=15,
):
    """
    Find this three-record pattern:
      1. Third record: Close < Open.
      2. Second record: Open > third record's Close, and Close > Open.
      3. Most recent record: Open > second record's Close, and Close > Open.

    Then inspect the following `lookahead_records` rows. Return each full
    follow-up row whose Close exceeds the pattern's final Close.

    Returns:
        matches: DataFrame of qualifying rows, with file/pattern metadata.
        any_match: True if any qualifying row was found.
    """
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, open_col, close_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_open"] = pd.to_numeric(df[open_col], errors="coerce")
        df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_open", "_close"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        # start is the third record; start + 1 and start + 2 are the
        # second and first records behind, respectively.
        for start in range(len(df) - 2):
            third = df.iloc[start]
            second = df.iloc[start + 1]
            last = df.iloc[start + 2]

            pattern_matches = (
                third["_close"] < third["_open"]
                and second["_open"] > third["_close"]
                and second["_close"] > second["_open"]
                and last["_open"] > second["_close"]
                and last["_close"] > last["_open"]
            )

            if not pattern_matches:
                continue

            pattern_end_idx = start + 2
            pattern_close = last["_close"]
            following = df.iloc[
                pattern_end_idx + 1 :
                pattern_end_idx + 1 + lookahead_records
            ]

            higher_rows = following[following["_close"] > pattern_close]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["pattern_date"] = last["_parsed_date"]
                result["pattern_close"] = pattern_close
                result["pct_change"] = round(((row["Close"] - pattern_close) / pattern_close) * 100, 2)
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty



def find_ma_crossover_followups(
    paths,
    ma_days=50,
    lookahead_records=15,
    date_col="Date",
    adj_close_col="Adj Close",
    close_col="Close",
):

   if ma_days < 1:
       raise ValueError("ma_days must be at least 1")
   if lookahead_records < 1:
       raise ValueError("lookahead_records must be at least 1")

   if isinstance(paths, (str, Path)):
       paths = [paths]

   results = []

   for path in paths:
       raw = pd.read_csv(path)

       required = {date_col, adj_close_col, close_col}
       missing = required - set(raw.columns)
       if missing:
           raise ValueError(
               f"{path}: missing columns {sorted(missing)}; "
               f"found {list(raw.columns)}"
           )

       original_columns = list(raw.columns)
       df = raw.copy()

       df["_parsed_date"] = pd.to_datetime(
           df[date_col], errors="coerce", utc=True
       )
       df["_adj_close"] = pd.to_numeric(df[adj_close_col], errors="coerce")
       df["_close"] = pd.to_numeric(df[close_col], errors="coerce")

       df = (
           df.dropna(subset=["_parsed_date", "_adj_close", "_close"])
             .sort_values("_parsed_date")
             .drop_duplicates("_parsed_date", keep="last")
             .reset_index(drop=True)
       )

       df["_moving_average"] = df["_adj_close"].rolling(
           window=ma_days,
           min_periods=ma_days,
       ).mean()

       previous_adj = df["_adj_close"].shift(1)
       previous_ma = df["_moving_average"].shift(1)

       # Crosses upward: previous Adj Close <= previous MA,
       # current Adj Close > current MA, and the MA is rising.
       crossover = (
           previous_adj.le(previous_ma)
           & df["_adj_close"].gt(df["_moving_average"])
           & df["_moving_average"].gt(previous_ma)
       )

       for signal_idx in df.index[crossover]:
           crossed_price = df.at[signal_idx, "_adj_close"]
           signal_date = df.at[signal_idx, "_parsed_date"]
           moving_average = df.at[signal_idx, "_moving_average"]

           following = df.iloc[
               signal_idx + 1 : signal_idx + 1 + lookahead_records
           ]
           higher_rows = following[following["_close"] > crossed_price]

           for _, row in higher_rows.iterrows():
               result = row[original_columns].to_dict()
               result["file"] = Path(path).name
               result["signal_date"] = signal_date
               result["signal_adj_close"] = crossed_price
               result["pct_change"] = round( ((row["Close"] - crossed_price) / crossed_price) * 100, 2)
               result["signal_moving_average"] = moving_average
               results.append(result)

   matches = pd.DataFrame(results)
   return matches, not matches.empty

def grid_search_ma_returns(
    csv_files,
    fast_periods=range(5, 21),
    slow_periods=range(20, 101, 5),
    date_col="Date",
    price_col="Adj Close",
    fee_bps=0.0,
):
    """
    Test fast/slow SMA combinations on each CSV.

    Returns a DataFrame with one row per file and MA-period pair,
    sorted by total strategy return within each file.

    Strategy: long when fast SMA > slow SMA; otherwise cash.
    """
    if isinstance(csv_files, (str, Path)):
        csv_files = [csv_files]

    fast_periods = sorted(set(fast_periods))
    slow_periods = sorted(set(slow_periods))
    pairs = [
        (fast, slow)
        for fast in fast_periods
        for slow in slow_periods
        if fast < slow
    ]
    if not pairs:
        raise ValueError("Provide at least one pair where fast_period < slow_period")

    fee_rate = fee_bps / 10_000
    results = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)

        missing = [c for c in [date_col, price_col] if c not in df.columns]
        if missing:
            raise ValueError(f"{csv_file}: missing columns {missing}")

        df[date_col] = pd.to_datetime(df[date_col], utc=True, errors="coerce")
        df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
        df = (
            df.dropna(subset=[date_col, price_col])
              .sort_values(date_col)
              .drop_duplicates(date_col, keep="last")
              .reset_index(drop=True)
        )

        prices = df[price_col]
        daily_returns = prices.pct_change().fillna(0.0)

        for fast, slow in pairs:
            fast_ma = prices.rolling(fast, min_periods=fast).mean()
            slow_ma = prices.rolling(slow, min_periods=slow).mean()

            # Create the signal at a close, then use it for the next record's return.
            signal = (fast_ma > slow_ma).where(slow_ma.notna(), False).astype(float)
            position = signal.shift(1).fillna(0.0)

            first_valid = slow_ma.first_valid_index()
            if first_valid is None:
                continue

            test_returns = daily_returns.loc[first_valid:]
            test_position = position.loc[first_valid:]

            # Charge costs when entering or leaving a position.
            turnover = test_position.diff().abs()
            if len(turnover):
                turnover.iloc[0] = abs(test_position.iloc[0])
            turnover = turnover.fillna(0.0)

            strategy_returns = test_position * test_returns - turnover * fee_rate
            total_return = (1.0 + strategy_returns).prod() - 1.0
            buy_hold_return = (1.0 + test_returns).prod() - 1.0
            entries = int((test_position.diff().fillna(test_position.iloc[0]) > 0).sum())

            results.append({
                "csv_name": Path(csv_file).name,
                "fast_period": fast,
                "slow_period": slow,
                "total_return": total_return,
                "buy_hold_return": buy_hold_return,
                "entries": entries,
                "records_tested": len(test_returns),
            })

    return (
        pd.DataFrame(results)
        .sort_values(["csv_name", "total_return"], ascending=[True, False])
        .reset_index(drop=True)
    )

