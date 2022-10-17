# Copyright 2019-2022 by Sergio Valqui. All rights reserved.

"""Test ssh to linux using netmiko
Works well to send commands that return the prompt
for commands that return continuous fails, tail-like, better use something else
`FAILED - RETRYING:`
"""
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

    svr_connect = ConnectHandler(**admin)
#    print(svr_connect.send_command("hostnamectl"))
#    print(net_connect.send_command("ceph status"))
##    print(svr_connect.send_command("rpm -qa tmux"))
#    print(svr_connect.send_command("df -h"))
    print(svr_connect.send_command("ls -la"))

    svr_connect.disconnect()


if __name__ == '__main__':
    sys.exit(main())
