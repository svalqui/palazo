import getpass
from lib.restapi.infobloxapi import IB

#script-user
user_name = input("Username: ")
password = getpass.getpass()
ipam_host = input("Ipam DNS name or IP: ")

page_networks = IB(user_name, password, ipam_host)
page_networks.page_handler()
