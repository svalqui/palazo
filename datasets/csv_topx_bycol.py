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