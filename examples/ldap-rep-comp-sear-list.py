# Copyright 2020 by Sergio Valqui. All rights reserved.
#
# Report Computers in an AD that match the look for string, list the computers (chosen attributes)
#
# # Run this in the command line while on the palazo directory so python can find serv
# export PYTHONPATH=`pwd`
# python3 examples/ldap-rep-comp-sear-list.py

from serv.ldaps import ldap_connect, find_computers_filtered, ldap_disconnect
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
    look_for = input("Search AD for :")

    user_password = getpass.getpass()

    connection = ldap_connect(URI, user_name, user_password)

    my_list = find_computers_filtered(BASE, connection, look_for,
                                      ["name", "operatingSystem", "operatingSystemVersion",
                                       "lastLogonTimestamp", "distinguishedName", "description",
                                       "userAccountControl"])
    # "userAccountControl" 4130 = Computer Disabled
    print(" ------       search concluded... printing ", len(my_list))
    for i in my_list:

        if isinstance(i, list):
            my_row = []
            for j in i:
                # print(j.header, j.content)
                if len(j.content) == 1:
                    value = j.content[0]
                    # print(j.content, " ", value)
                else:
                    value = "Multiple Values"
                    # print(j.content)
                my_row.append(value)
            print("\t".join(my_row))
        else:
            print(i)
            print(i.header, i.content)

    ldap_disconnect(connection)
