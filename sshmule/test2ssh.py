# Copyright 2019-2022 by Sergio Valqui. All rights reserved.


import sys
# from netmiko import ConnectHandler
import logging
import paramiko
from paramiko_expect import SSHClientInteraction


def main():
    my_pkey = paramiko.agent.Agent().get_keys()[0]
    logging.basicConfig(filename="/home/sergio/sshtest2debug.log", level=logging.DEBUG)
    logger = logging.getLogger("netmiko")

    svr_admin = input("svr_admin :")

    admin = {
        "device_type": "linux",
        "host": svr_admin,
        "username": "root",
        "allow_agent": True,
        "pkey": my_pkey,
        "global_delay_factor": 2,
    }

    svr_connect = ConnectHandler(**admin)
##    print(svr_connect.send_command("rpm -qa tmux"))
    print (svr_connect.send_command_expect("ls -la", expect_string="bash_history"))
#    print(svr_connect.send_command(command_string="ls -la", expect_string="bash_history"))

    svr_connect.disconnect()


if __name__ == '__main__':
    sys.exit(main())
