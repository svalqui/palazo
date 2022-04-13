import configparser
import pathlib
import sys

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
    print("getting ", ticket)
    cia_his = yf.download(ticket, period="2y")
    print(his_path / ticket)
    cia_his.to_csv(his_path / ticket)


if __name__ == '__main__':
    sys.exit(main())

