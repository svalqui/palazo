import pandas as pd


def validate_codes(csv_file, col_name):
    df = pd.read_csv(
        csv_file,
        dtype={col_name: "string"}
    )

    codes = (
        df[col_name]
        .str.strip()
        .str.upper()
    )

    has_blank_codes = codes.isna() | codes.eq("")
    duplicate_codes = codes[codes.duplicated(keep=False)]

    valid = True

    if has_blank_codes.any():
        print("Rows with missing codes:")
        print(df[has_blank_codes].to_string(index=False))
        valid = False

    if not duplicate_codes.empty:
        print("\nDuplicate codes:")
        print(sorted(duplicate_codes.dropna().unique()))
        valid = False

    if valid:
        print("All codes are present and unique.")

    return valid
