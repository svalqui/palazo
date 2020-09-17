# Copyright 2020 by Sergio Valqui. All rights reserved.
#
# Report Computers in an AD that match the look for string, and list all attributes of the computers matching
#
# Run this in the command line while on the palazo directory so python can find serv
# export PYTHONPATH=`pwd`
# python3 examples/ldap-rep-comp-sear-att.py

from serv.ldaps import ldap_connect, find_computers, ldap_disconnect, modify_replace
from ldap3 import MODIFY_REPLACE
# from pathlib import Path
# import datetime
import getpass
import configparser
import pathlib


file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Reading configuration
config = configparser.ConfigParser()

user_name = ''
URI = ''

try:
    config.read(str(file_conf_name))
    user_name = config['Settings']['default_user']
    URI = config['Settings']['uri']
    BASE = config['Settings']['default_base']
    show_fields = config['Filters']['show_attributes'].split(',')
    proceed = True

except BaseException as e:
    print('--FileError: ', e)
    print('--Exception Name :', type(e))
    proceed = False

if proceed:
    my_computer = input("Comp  Name (Unique) :")

    user_password = getpass.getpass()

    connection = ldap_connect(URI, user_name, user_password)

    det_list = find_computers(BASE, connection, my_computer)
    existing_des = ''
    new_des = "added to des"
    # "distinguishedName"
    d_name = ''

    for i in det_list:
        print('det_list len ',len(det_list))
        # TODO verify that the attributes exists, if not it will need to be created.
        if isinstance(i, list):
            for j in i:
                if j.header == 'description':
                    print('description ', j.content[0])
                    existing_des = j.content[0]
                if j.header == 'userAccountControl':
                    print('userAccountControl', j.content[0])
                    existing_uac = j.content[0]
                if j.header == 'distinguishedName':
                    print('distinguishedName', j.content[0])
                    d_name = j.content[0]
            print()

    #                        change = {'description': [(MODIFY_REPLACE, [new_des])],
    #                                  'UserAccountControl': [(MODIFY_REPLACE, ['2'])]}

    new_des = existing_des + " " + new_des
    # New UserAccountControl 2, Account Disabled
    new_uac = str(int(existing_uac) | 2)

    print("uac ", new_uac, " d_name ", d_name, " new_des ", new_des)

    change = {'description': [(MODIFY_REPLACE, [new_des])], 'UserAccountControl': [(MODIFY_REPLACE, [new_uac])]}

    modify_replace(connection, d_name, change, True)

    ldap_disconnect()
