# Copyright 2019-2022 by Sergio Valqui. All rights reserved.
# ssh to multiple host, base pipeliner

# Example with Paramiko using ubikey
# import paramiko
# pkey = paramiko.agent.Agent().get_keys()[0]
# host = "my-host"
# client = paramiko.SSHClient()
# policy = paramiko.AutoAddPolicy()
# client.set_missing_host_key_policy(policy)
# client.connect(host, username="root", look_for_keys=True, pkey=pkey)
# _stdin, stdout, _stderr = client.exec_command("hostnamectl")
# lines = stdout.read().decode()
# print(lines)
# client.close()
#
#
#
# Exmple Netmiko using ubikey
# my_pkey = paramiko.agent.Agent().get_keys()[0]
# svr_admin = "my_host"
# svr_node = input("svr_node :")
# admin = {
#     "device_type": "linux",
#     "host": svr_admin,
#     "username": "root",
#     "allow_agent": True,
#     "pkey": my_pkey,
#     "global_delay_factor": 2,
# }
#
# net_connect = ConnectHandler(**admin)
# print(net_connect.send_command("hostnamectl"))
# net_connect.disconnect()

