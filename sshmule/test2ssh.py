# Copyright 2019-2022 by Sergio Valqui. All rights reserved.


import sys
# from netmiko import ConnectHandler
import logging
import paramiko
import traceback
from paramiko_expect import SSHClientInteraction


def main():
    my_pkey = paramiko.agent.Agent().get_keys()[0]
    logging.basicConfig(filename="/home/sergio/sshtest2debug.log", level=logging.DEBUG)
    logger = logging.getLogger("netmiko")

    svr_admin = input("svr_admin :")
    PROMPT = input("Prompt to expect:")

    admin = {
        # "device_type": "linux",
        "hostname": svr_admin,
        "username": "root",
        "allow_agent": True,
        "pkey": my_pkey,
        # "global_delay_factor": 2,
    }

    cmd_output_uname = ""

    try:
        client = paramiko.SSHClient()

        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(**admin)

        with SSHClientInteraction(client, timeout=10, display=True) as interact:
            interact.expect(PROMPT)

            # Run the first command and capture the cleaned output, if you want
            # the output without cleaning, simply grab current_output instead.
            interact.send('ls -l')
            interact.tail(stop_callback=lambda x: 'SAS-Drive_Firmware' in x)
            cmd_output_uname = interact.current_output_clean

    except Exception:
        traceback.print_exc()
    finally:
        try:
            client.close()
        except Exception:
            pass

    print(cmd_output_uname)


if __name__ == '__main__':
    sys.exit(main())
