# Copyright 2019-2023 by Sergio Valqui. All rights reserved.

import sys
import logging
import paramiko
import time


def osdnodes(admin_connection):
    """Returns a list of osd server nodes"""
    osd_nodes = []
    output = admin_connection.send_command("ceph osd tree | grep host")
    # print("output type: ", type(output))
    for line in output.splitlines():
        osd_nodes.append(line.split()[-1])
    # print(osd_nodes)

    return osd_nodes


def osversion(connection):
    """Returns the OS version from hostnamectl"""
    output = connection.send_command("hostnamectl")
    os_version = ""
    for line in output.splitlines():
        if line.find("Operating System:") > -1:
            os_version = line.split(":")[1].strip()

    if len(os_version) == 0:
        os_version = "OS Version not found"

    return os_version


def main():
    my_pkey = paramiko.agent.Agent().get_keys()[0]
    logging.basicConfig(filename="/home/sergio/sshdebugceph78.log", level=logging.DEBUG)

    svr_domain = input("server domain name :")
    svr_domain = "." + svr_domain
    svr_admin = input("svr_ceph_admin :")
    svr_monitor = input("svr_ceph_monitor :")

    # TODO commands returning nothing cause "raise socket.error("Socket is closed")" on paramiko

    admin = {
        "device_type": "linux",
        "host": svr_admin + svr_domain,
        "username": "root",
        "allow_agent": True,
        "pkey": my_pkey,
        "global_delay_factor": 2,
    }
    admin_connect = ConnectHandler(**admin)
    print(admin_connect.send_command("ceph status"))
    my_nodes = osdnodes(admin_connect)
    admin_connect.disconnect()

    for osd_node in my_nodes:
        node = {
            "device_type": "linux",
            "host": osd_node + svr_domain,
            "username": "root",
            "allow_agent": True,
            "pkey": my_pkey,
            "global_delay_factor": 2,
        }
        node_connect = ConnectHandler(**node)
        # time.sleep(0.1)
        print("---On :", osd_node + svr_domain)
        # print(osversion(node_connect))
        print(node_connect.send_command("hostnamectl"))
        # print(admin_connect.send_command("rpm -qa tmux"))
        print(node_connect.send_command_timing("df -h"))

        node_connect.disconnect()


if __name__ == '__main__':
    sys.exit(main())
