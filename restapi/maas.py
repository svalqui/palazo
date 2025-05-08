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
                  )

def machine_list_virsh(client):
    for m in client.machines.list():
        if m.power_type == 'virsh':
            print(m.fqdn,
                  m.distro_series,
                  m.power_type,
                  m.cpus,
                  m.memory,
                  m.power_state,
                  m.ip_addresses,
                  )


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

    exit()


    for m in client.machines.list():
        # print(dir(m))
        # print(m.architecture)
        # print(m.boot_disk)
        # print(m.node_type)
        # print(m.power_state)
        # print(m.cpus)
        # print(m.memory)
        # print("power_type", m.power_type)

        # print(m.get_details())
        # dict_keys(['lldp', 'lshw'])
        # print(m.get_details()['lldp'])
        # print(m.get_details()['lshw'])
        m_details = m.get_details()
        # print(m_details['lshw'])
        # print(type(m_details['lshw'].decode()))
        if "qh2-rc" not in m.hostname:
            if m.status.name == "DEPLOYED":
#                if m.distro_series != "jammy":
                if m.distro_series == "jammy":
                    print(m.fqdn,
                          # m.hostname,
                          m.distro_series,
                          m.power_type,
                          m.cpus,
                          m.memory,
                          # m.zone,
                          #m.pool,
                          m.ip_addresses,
                          )
                    # print(type(m.status))


# Get a reference to self.
    myself = client.users.whoami()

    print(myself)
    assert myself.is_admin, "%s is not an admin" % myself.username


if __name__ == '__main__':
    sys.exit(main())
