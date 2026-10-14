# Copyright 2019-2026 by Sergio Valqui. All rights reserved.
#python fin/hcoll.py code
import argparse
import configparser
import pathlib
import sys
from datetime import datetime, date

import yfinance as yf


def normalize_asx_code(code):
    """Convert to standard ASX code."""

    code = str(code).strip().upper()

    if not code:
        raise ValueError("code cannot be empty")

    if not code.endswith(".AX"):
        code = f"{code}.AX"

    return code

def get_hist(ticker, hisfile_path):
    print("Downloading:", ticker)

    dat = yf.Ticker(ticker)

    cia_his = dat.history(
        period="5y",
        interval="1d",
        auto_adjust=False,
    )

    if cia_his.empty:
        raise RuntimeError(
            f"No data returned for {ticker}"
        )

    cia_his.to_csv(hisfile_path)

    print(f"Saved {len(cia_his)} rows to {hisfile_path}")


def main(code):
    file_conf_dir = pathlib.Path.home()
    print("file_conf_dir:", file_conf_dir)

    his_path = file_conf_dir/ "ASX" / "hist"
    print("his_path:", his_path)
    his_path.mkdir(parents=True, exist_ok=True)

    # Convert code to AX code for yfinance
    ticker = normalize_asx_code(code)

    hisfile_path = his_path / ticker

    print("Getting:", ticker)
    print("Histfile path:", hisfile_path)

    if hisfile_path.exists():
        modified_date = datetime.fromtimestamp(
            hisfile_path.stat().st_mtime
        ).date()

        if modified_date != date.today():
            print("File is not from today; downloading it.")
            get_hist(ticker, hisfile_path)
        else:
            print("File is from today; skipping download.")
            return 0
    else:
        print("File does not exist; downloading it.")
        get_hist(ticker, hisfile_path)
    return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download data"
    )

    parser.add_argument(
        "code",
        help="Give it a code",
    )

    args = parser.parse_args()

    sys.exit(main(args.code))



