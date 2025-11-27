
#!/usr/bin/env python

import configparser
import pathlib
from os import path
import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import maas.client

from tools.util_obj import print_structure_det


def machine_list_all(client):
    for m in client.machines.list():
        print(m.fqdn,
              # m.hostname,
              m.distro_series,
              m.power_type,
              m.cpus,
              m.memory,
              # m.zone,
              # m.pool,
              m.power_state,
              m.ip_addresses,
              m.status,
              m._data['pod']['name'],
              )

def machine_list_ipmi(client):
    for m in client.machines.list():
        if m.power_type == 'ipmi':
            print(m.fqdn,
                  m.distro_series,
                  m.power_type,
                  m.cpus,
                  m.memory,
                  m.power_state,
                  m.ip_addresses,
                  m.status,
                  m._data['pod']['name'],
                  )

def machine_list_virsh(client):
    for m in client.machines.list():
        if m.power_type == 'virsh':
            # det = m.get_details()
            print(m.fqdn,
                  m.osystem,
                  m.distro_series,
                  m.power_type,
                  m.cpus,
                  m.memory,
                  m.power_state,
                  m.ip_addresses,
                  m.pool.name,
                  m.status,
                  m.zone.name,
                  m._data['pod']['name'],
                  )

def none_attr():
    print("  is None")

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

    kvms = client.pods.list()

    print(kvms)

    print(dir(kvms[0]))
    print(kvms[0])

    for i in dir(kvms[0]):
        print(i)
        if i == "_data":
            print(getattr(kvms[0],i))

    print()

    for k in kvms:
        print(k.name)

    print(" select what to do: \n"
          "(a) list all machines \n"
          "(ipmi) list all ipimi machines \n"
          "(virsh) list all virtual machine \n")

    option = input("select your option: ")

    if option == 'a':
        machine_list_all(client)
    elif option == 'ipmi':
        machine_list_ipmi(client)
    elif option == 'virsh':
        machine_list_virsh(client)


# Get a reference to self.
    myself = client.users.whoami()

    print(myself)
    assert myself.is_admin, "%s is not an admin" % myself.username


if __name__ == '__main__':
    sys.exit(main())
