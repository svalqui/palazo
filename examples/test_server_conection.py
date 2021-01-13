# # Run this in the command line while on the palazo directory so python can find serv
# export PYTHONPATH=`pwd`
# python3 examples/test_server_connection.py

import pathlib
import configparser
import getpass
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, MODIFY_REPLACE

file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Reading configuration
print("reading configuration file...")
config = configparser.ConfigParser()
config.read(str(file_conf_name))
user_name = config['Settings']['default_user']
print("user_name", user_name)
URI = config['Settings']['uri']
print("URI", URI)
BASE = config['Settings']['default_base']
print("BASE", BASE)
show_fields = config['Filters']['show_attributes'].split(',')

user_password = getpass.getpass()

#  First connection bind
try:
    print("1 === Trying bind no authentication")
    server = Server(URI, use_ssl=True, get_info=ALL)
    ldap_connection = Connection(server, auto_bind=True)
    print("ldap connection")
    print(ldap_connection)
    print(" Server.info")
    print(server.info)
    ldap_connection.unbind()
except BaseException as ldap_connection_error:
    print(ldap_connection_error)

#  Connection with username
try:
    print()
    print("2 === Trying bind username/password")
    server = Server(URI, use_ssl=True, get_info=ALL)
    ldap_connection = Connection(server, user=user_name, password=user_password,  auto_bind=True)
    print("ldap connection")
    print(ldap_connection)
    print(" Server.info")
    print(ldap_connection.extend.standard.who_am_i())
    ldap_connection.unbind()
except BaseException as ldap_connection_error:
    print("user_name", user_name)
    print("URI", URI)
    print("BASE", BASE)
    print(ldap_connection_error)
