#!/usr/bin/env python

import configparser
import pathlib
from os import path
import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import maas.client

from tools.util_obj import print_structure_det
def main():
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()
    config.read(str(file_conf_name))
    maas_url = config['maas']['url']
    maas_apikey = config['maas']['apikey']

    client = maas.client.connect( maas_url, apikey=maas_apikey)

# Get a reference to self.
    myself = client.users.whoami()
    print(myself)
    assert myself.is_admin, "%s is not an admin" % myself.username

    for m in client.machines.list():
        print(repr(m))
        print("To print structure detailed")
        print()
        print(m.hostname)
        print(m.zone)
        print(m.zone.name)
        print(m.zone.virtualblockdevice_set)
        for i in m.zone:
            print (i)
        #print_structure_det(m, True)

        break



if __name__ == '__main__':
    sys.exit(main())
