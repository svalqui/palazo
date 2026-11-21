import pandas as pd


def print_top_x_by_col(csv_file, how_many, col_name):
    df = pd.read_csv(
        csv_file,
        dtype={col_name: "string"}
    )

    # Normalize codes
    df[col_name] = (
        df[col_name]
        .str.strip()
        .str.upper()
    )

    # Convert Col into a number
    #
    df["_col_numeric"] = pd.to_numeric(
        df[col_name]
        .astype("string")
        .str.replace(r"[^\d.-]", "", regex=True),
        errors="coerce"
    )

    # Sort largest first and select the top x
    top_x = (
        df.dropna(subset=["_col_numeric"])
        .sort_values(
            by="_col_numeric",
            ascending=False
        )
        .head(how_many)
        .drop(columns=["_col_numeric"])
    )

    #print(top_x.to_string(index=False, header=False))

    return top_x.values.tolist()

def print_top_x_per_group(csv_file, how_many, col_name, group_col):
    df = pd.read_csv(csv_file, dtype={col_name: "string"})

    # Normalize and convert the ranking column to numbers
    df[col_name] = df[col_name].str.strip().str.upper()
    df["_col_numeric"] = pd.to_numeric(
        df[col_name].str.replace(r"[^\d.-]", "", regex=True),
        errors="coerce",
    )

    top_x = (
        df.dropna(subset=["_col_numeric"])
          .sort_values("_col_numeric", ascending=False)
          .groupby(group_col, dropna=False, sort=False)
          .head(how_many)
          .drop(columns=["_col_numeric"])
    )

    return top_x.values.tolist()

def add_rank_column(input_csv, value_column, output_csv=None):
    """Add a sequential Rank column; highest value gets rank 1."""
    df = pd.read_csv(input_csv)

    # Ensure values sort numerically, even if the CSV column was read as text.
    values = pd.to_numeric(df[value_column], errors="coerce")

    # Rank numeric values first; largest gets rank 1.
    numeric_ranks = values.rank(method="first", ascending=False)

    # Put missing or "--" values after all numeric rows.
    missing = values.isna()
    numeric_count = (~missing).sum()
    numeric_ranks.loc[missing] = range(
        numeric_count + 1,
        numeric_count + missing.sum() + 1
    )

    df["Rank"] = numeric_ranks.astype(int)

    # If no output path is given, update the input file.
    df.to_csv(output_csv or input_csv, index=False)
    return df