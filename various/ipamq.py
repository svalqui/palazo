# Copyright 2019-2023 by Sergio Valqui. All rights reserved.


import configparser
import ipaddress
import pathlib
from os import path
import sys


# from restapi.infobloxapi import IB
from infoblox_client import connector, objects, utils, exceptions

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

import urllib3

# Remove: InsecureRequestWarning: Unverified HTTPS request is being made to host
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from tools.util_obj import print_structure
from tools.util_obj import print_structure_det
from tools.util_obj import look_for_obj_by_att_val


def ipam_connect(ipam_opts):
    ipam_connector = connector.Connector(ipam_opts)
    return ipam_connector

def q_ip(my_ip, my_connector):
    """Query IP"""
    return_ip = objects.IPv4Address.search_all(
        my_connector,
        ip_address=my_ip,
    )

    # print(return_ip)
    # print(type(return_ip))
    # print(len(return_ip))
    for i in return_ip:
        return_net = objects.Network.search_all(
            my_connector,
            network=i.network
        )
        # print(return_net)
        # print_structure_det(return_net, )
        # print(i)
        for net in return_net:
            ret_net_ip = ipaddress.ip_network(net.cidr)
            print("ip", my_ip)
            print("cidr:", net.cidr)
            print("netmask:",ret_net_ip.netmask)
            print("gateway",ret_net_ip.network_address + 1)
            print("range:",
                  ret_net_ip.network_address,
                  "-",
                  ret_net_ip.broadcast_address,
                  "(",
                  ret_net_ip.num_addresses,
                  "addresses",
                  ")",
            )
            if i.mac_address != "":
                print("mac:", i.mac_address)
            print("comment:",net.comment)

            my_ea_keys = net.extattrs._ea_dict.keys()
            if 'Zone' in my_ea_keys:
                print("zone:", net.extattrs._ea_dict['Zone'])
            if 'VLAN' in my_ea_keys:
                print("vlan:", net.extattrs._ea_dict['VLAN'])
            if 'VRF' in my_ea_keys:
                print("vrf:", net.extattrs._ea_dict['VRF'])

            print("status:", i.status)
            print("Types of records associated with this IP:", i.types)
            my_names = ", ".join(i.names)
            print(my_ip, my_names)

def q_net(my_cidr, my_connector):
    """Query Network"""

    my_nets =objects.Network.search_all(
        my_connector,
        network=my_cidr,
    )
    for net in my_nets:
        # Get Network IPs
        network_ips = objects.IPv4Address.search_all(
            my_connector,
            network=my_cidr,
            paging=True,
        )
        ret_net_ip = ipaddress.ip_network(net.cidr)
        print("cidr:", net.cidr)
        print("netmask:", ret_net_ip.netmask)
        print("gateway", ret_net_ip.network_address + 1)
        print("range:",
              ret_net_ip.network_address,
              "-",
              ret_net_ip.broadcast_address,
              "(",
              ret_net_ip.num_addresses,
              "addresses",
              ")",
              )
        my_ea_keys = net.extattrs._ea_dict.keys()
        if 'Zone' in my_ea_keys:
            print("zone:", net.extattrs._ea_dict['Zone'])
        if 'VLAN' in my_ea_keys:
            print("vlan:", net.extattrs._ea_dict['VLAN'])
        if 'VRF' in my_ea_keys:
            print("vrf:", net.extattrs._ea_dict['VRF'])
        print()

        for subset_ips in utils.paging(network_ips, max_results=256):
            for i in subset_ips:
                my_display = i.status
                if i.status != "UNUSED":
                    my_display = ", ".join(i.names)
                    if "RESERVATION" in i.types:
                        my_display = 'RESERVATION'
                    elif "UNMANAGED" in i.types:
                        my_display = 'UNMANAGED'
                print(i.ip_address, my_display)


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

    print("(i) look for IP address \n"
          "(n) look for network cidr \n"
          "(tba) tba\n")

    look_in = input("your choice: ")
    look_for = input("Search for :")

    if look_in == "i": # Look for ip
        print()
        q_ip(look_for, my_connection)
    elif look_in == "n": # look for network by cidr
        print()
        q_net(look_for, my_connection)
    else:
        print("No option available")


if __name__ == '__main__':
    sys.exit(main())
