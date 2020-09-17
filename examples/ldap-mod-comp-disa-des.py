# Copyright 2020 by Sergio Valqui. All rights reserved.
#
# Modify computers, disables computers that lastLogonTimestamp is more than 2 years old and add a time stamp on
# the description
#
# Run this in the command line while on the palazo directory so python can find serv
# export PYTHONPATH=`pwd`
# python3 examples/ldap-rep-comp-sear-att.py

from serv.ldaps import ldap_connect, find_generic, ldap_disconnect, modify_replace
from ldap3 import MODIFY_REPLACE  # TODO find a way to fit this on ldaps.py
from pathlib import Path
import datetime as dt
import getpass
import configparser
import pathlib

# LDAP Configuration file 2 directories up
#
file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Log file and time stamps
#
time_now = dt.datetime.now()
year = dt.timedelta(days=365)
two_years_ago = time_now - 2 * year
two_ya_ldap = two_years_ago.strftime("%Y%m%d%H%M%S") + ".0Z"

# File name for the log
log_file_name = 'log-ldap-mod-des' + time_now.strftime('-%Y%m%d-%H%M%S') + '.txt'
path = Path.home()
full_log_filename = path / log_file_name
ff_log_file = open(full_log_filename, 'w')

# Description to added existing description, time stamp on description
des_stamp = "Science IT Disabled " + time_now.strftime('%b %Y')

# Reading configuration
config = configparser.ConfigParser()

user_name = ''
URI = ''

try:
    config.read(str(file_conf_name))
    user_name = config['Settings']['default_user']
    URI = config['Settings']['uri']
    base = config['Settings']['default_base']
    show_fields = config['Filters']['show_attributes'].split(',')
    proceed = True

except BaseException as e:
    print('--FileError: ', e)
    print('--Exception Name :', type(e))
    proceed = False

if proceed:
    ad_ou = input("Distinguished name of AD OU where computers will be search :")

    user_password = getpass.getpass()

    connection = ldap_connect(URI, user_name, user_password)

    # Find all computers on the AD OU, 2 years older, enabled
    # "lastLogonTimestamp"
    query = '(&(objectcategory=computer)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(lastLogonTimestamp<=' + two_ya_ldap + '))'
    comp_list = find_generic(ad_ou, connection, query)

    # Dictionary holder of current computer attributes, to be changed ("description", "userAccountControl")
    # note: "name", "distinguishedName", "description", "userAccountControl"
    dic_comp_cur_det = {}

    for i in comp_list:
        print('det_list len ', len(comp_list))
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


    existing_des = ''
    new_des = "added to des"
    # "distinguishedName"
    d_name = ''




    new_des = existing_des + " " + new_des
    # New UserAccountControl 2, Account Disabled
    new_uac = str(int(existing_uac) | 2)

    print("uac ", new_uac, " d_name ", d_name, " new_des ", new_des)

    change = {'description': [(MODIFY_REPLACE, [new_des])], 'UserAccountControl': [(MODIFY_REPLACE, [new_uac])]}

    modify_replace(connection, d_name, change, True)

    ldap_disconnect()
