# Copyright 2019-2023 by Sergio Valqui. All rights reserved.


import configparser
import pathlib
import sys

# from restapi.infobloxapi import IB
from infoblox_client import connector
from infoblox_client import objects
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def ipam_connect(ipam_opts):
    ipam_connector = connector.Connector(IPAM_OPTS)
    return ipam_connector

def q_ip(my_ip, my_connector):
    """Query IP"""

def q_net(my_cidr, my_connector):
    """Query Network"""

def main():
    """Testing infoblox_client"""
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()
    config.read(str(file_conf_name))
    ipam_host = config['infoblox']['IPAM_HOST']
    ipam_username = config['infoblox']['IPAM_USERNAME']
    ipam_password = config['infoblox']['IPAM_PASSWORD']

    ipam_opts = {
        'host': ipam_host,
        'username': ipam_username,
        'password': ipam_password,
    }

    my_connection = ipam_connect(ipam_opts)


if __name__ == '__main__':
    sys.exit(main())
