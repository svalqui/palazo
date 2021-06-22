# Copyright 2021 by Sergio Valqui. All rights reserved.
import pathlib
import sys

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
        os_user_name = config['openstack']['OS_USERNAME']
        print(os_user_name)
        os_user_pass = config['openstack']['OS_PASSWORD']
        os_version = config['openstack']['OS_API_VERSION']
        os_project_id = config['openstack']['OS_PROJECT_ID']
        os_project_name = config['openstack']['OS_PROJECT_NAME']
        os_auth_url = config['openstack']['OS_AUTH_URL']
        os_user_domain = config['openstack']['OS_USER_DOMAIN_NAME']

        proceed = True

    except BaseException as e:
        print('--FileError: ', e)
        print('--Exception Name :', type(e))
        proceed = False

    if proceed:
        nova = client.Client(version=os_version, username=os_user_name, password=os_user_pass,
                             project_id=os_project_id, auth_url=os_auth_url, user_domain_name=os_user_domain)
        l = nova.servers.list()
        print(dir(l[0]))
        print(l)
        for instance in nova.servers.list():
            print(instance.name, instance.addresses)
        print(nova.flavors.list())



if __name__ == '__main__':
    sys.exit(main())




