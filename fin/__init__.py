# Copyright 2019-2022 by Sergio Valqui. All rights reserved.
"""Uses https://pypi.org/project/yfinance/

"""

import sys

def IsAuMrkO(self):

    opened = False

#  https://www.asx.com.au/

    import requests
    from bs4 import BeautifulSoup

    # Collect and parse page
    page = requests.get('https://www.asx.com.au')
    soup = BeautifulSoup(page.text, 'html.parser')

    return opened


def doti(code, hist_dir, debug=0):
    """Format
                  Open    High     Low   Close      Volume  Dividends  Stock Splits
Date
1986-03-13    0.06    0.06    0.06    0.06  1031788800        0.0           0.0
"""
    import yfinance as yf

    filename = hist_dir + code + ".txt"

    # If file exists
    # start last date, end today

    # Else = max

    code = yf.Ticker("code")
    hist = code.history(period="max")


def main():


if __name__ == '__main__':
    sys.exit(main())



    