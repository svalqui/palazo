# Copyright 2019-2022 by Sergio Valqui. All rights reserved.


import sys
from netmiko import ConnectHandler
import logging
import paramiko


def main():
    my_pkey = paramiko.agent.Agent().get_keys()[0]
    logging.basicConfig(filename="/home/sergio/sshdebug.log", level=logging.DEBUG)
    logger = logging.getLogger("netmiko")

    svr_admin = input("svr_admin :")
    svr_node = input("svr_node :")

    admin = {
        "device_type": "linux",
        "host": svr_admin,
        "username": "root",
        "allow_agent": True,
        "pkey": my_pkey,
        "global_delay_factor": 2,
    }

    net_connect = ConnectHandler(**admin)
    print(net_connect.send_command("hostnamectl"))
#    print(net_connect.send_command("ceph status"))
    print(net_connect.send_command("rpm -qa tmux"))
    net_connect.disconnect()


if __name__ == '__main__':
    sys.exit(main())
