# Copyright 2021 by Sergio Valqui. All rights reserved.
from novaclient import client
from cinderclient import client as cinder_client
from time import sleep
import platform
import subprocess
import argparse
import configparser


def main():
    """ CLI implementation temporal for fast trial while developing
    it requires palazo.ini 2 directories up with configuration as follow
    --- palazo.ini ---
    [openstack]
    OS_AUTH_URL=https://
    OS_PROJECT_ID=
    OS_PROJECT_NAME=
    OS_USERNAME="username@domain.org"
    OS_PASSWORD=
    OS_REGION_NAME="Melbourne"
    --- end of palazo.ini ---
    :return:
    """

    # Removing configuration from Project, configuration file 'palazo.ini' moved 2 directories up
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()

    try:
        config.read(str(file_conf_name))
        user_name = config['openstack']['OS_USERNAME']
        version = config['openstack']['OS_API_VERSION']
        user_pass = config['openstack']['OS_PASSWORD']
        project_id = config['openstack']['OS_PROJECT_ID']
        auth_url = config['openstack']['OS_AUTH_URL']
        proceed = True

    except BaseException as e:
        print('--FileError: ', e)
        print('--Exception Name :', type(e))
        proceed = False

