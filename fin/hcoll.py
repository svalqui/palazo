import configparser
import pathlib
import sys

import pandas as pd
import yfinance as yf


def main():
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()
    config.read(str(file_conf_name))
    main_path = config['fin']['homedir']
    his_path = pathlib.Path(main_path) / 'hist'
    print(his_path)

    ticket = input("T? :")
    print("getting :", ticket)
    # If file exist get the latest date
    hisfile_path = his_path / ticket
    print("Histfile path :",hisfile_path)
    if hisfile_path.expanduser().exists():
        print("File exists")
        # get most recent date
        cur_hist = pd.read_csv(hisfile_path, index_col=['Date'], parse_dates=['Date'])
        cur_hist.info()

    else:
        print("Download:", ticket)
        cia_his = yf.download(ticket, period="2y")
        print(hisfile_path)
        cia_his.to_csv(hisfile_path)


if __name__ == '__main__':
    sys.exit(main())

