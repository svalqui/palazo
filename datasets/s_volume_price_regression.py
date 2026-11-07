from pathlib import Path

import pandas as pd


def find_volume_price_runs(
    paths,
    date_col="Date",
    price_col="Close",
    volume_col="Volume",
    consecutive_increases=3,
    lookahead_records=15,
):
    if consecutive_increases < 1:
        raise ValueError("consecutive_increases must be at least 1")
    if lookahead_records < 1:
        raise ValueError("lookahead_records must be at least 1")

    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []

    for path in paths:
        raw = pd.read_csv(path)

        required = {date_col, price_col, volume_col}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"{path}: missing columns {sorted(missing)}; "
                f"found {list(raw.columns)}"
            )

        original_columns = list(raw.columns)
        df = raw.copy()

        # utc=True handles timestamps with differing timezone offsets.
        df["_parsed_date"] = pd.to_datetime(
            df[date_col], errors="coerce", utc=True
        )
        df["_price"] = pd.to_numeric(df[price_col], errors="coerce")
        df["_volume"] = pd.to_numeric(df[volume_col], errors="coerce")

        df = (
            df.dropna(subset=["_parsed_date", "_price", "_volume"])
              .sort_values("_parsed_date")
              .drop_duplicates("_parsed_date", keep="last")
              .reset_index(drop=True)
        )

        price_up = df["_price"].diff().gt(0)
        volume_up = df["_volume"].diff().gt(0)

        price_run = (
            price_up.rolling(consecutive_increases)
            .sum()
            .eq(consecutive_increases)
        )
        volume_run = (
            volume_up.rolling(consecutive_increases)
            .sum()
            .eq(consecutive_increases)
        )

        run_end_indices = df.index[price_run & volume_run]

        for end_idx in run_end_indices:
            signal_price = df.at[end_idx, "_price"]
            signal_date = df.at[end_idx, "_parsed_date"]

            # The rows immediately after the run; up to 15 by default.
            following = df.iloc[
                end_idx + 1 : end_idx + 1 + lookahead_records
            ]

            # Compare each follow-up price with the price at the run's end.
            higher_rows = following[following["_price"] > signal_price]

            for _, row in higher_rows.iterrows():
                result = row[original_columns].to_dict()
                result["file"] = Path(path).name
                result["signal_date"] = signal_date
                result["signal_price"] = signal_price
                results.append(result)

    matches = pd.DataFrame(results)
    return matches, not matches.empty
