# Copyright 2019-2023 by Sergio Valqui. All rights reserved.


import getpass
from restapi.infobloxapi import IB

#script-user
user_name = input("Username: ")
password = getpass.getpass()
ipam_host = input("Ipam DNS name or IP: ")

page_networks = IB(user_name, password, ipam_host, "network")
page_networks.get_page_handler()
#page_networks.post_page()
