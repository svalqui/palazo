import getpass
from lib.restapi.infobloxapi import IB


user_name = getpass.getpass("Username: ")
password = getpass.getpass()

page_networks = IB(user_name, password).page.text
