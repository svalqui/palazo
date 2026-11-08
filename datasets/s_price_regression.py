from pathlib import Path

import pandas as pd


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
               result["signal_moving_average"] = moving_average
               results.append(result)

   matches = pd.DataFrame(results)
   return matches, not matches.empty
