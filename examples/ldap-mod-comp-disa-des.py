# Copyright 2020 by Sergio Valqui. All rights reserved.
#
# Modify computers, disables computers that lastLogonTimestamp is more than 2 years old and adds a time stamp on
# the description, on an AD distinguished name branch.
#
# AD dist_name format: OU=Workstations,OU=my_classification_of_sub_units,OU=my_sub_units,DC=my_business,DC=com,DC=au
#
# Run this in the command line while on the palazo directory so python can find serv
# export PYTHONPATH=`pwd`
# python3 examples/ldap-rep-comp-sear-att.py

from serv.ldaps import ldap_connect, find_generic, ldap_disconnect, modify_replace
from ldap3 import MODIFY_REPLACE  # TODO find a way to fit this on ldaps.py
from pathlib import Path
import datetime as dt
import time
import getpass
import configparser
import pathlib

# LDAP Configuration file, ldapq.ini, 2 directories up
#
file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Log file and time stamps
# Log file set to home directory
#
time_now = dt.datetime.now()
two_year = dt.timedelta(days=730)
two_years_ago_ts = time_now - two_year
two_years_ago_ldap = (time.mktime(two_years_ago_ts.timetuple()) + 11644473600) * 10000000
twa_ldap_str = str(int(two_years_ago_ldap))

print("two_years_ago_ts", two_years_ago_ts)
print("two_years_ago_ldap", two_years_ago_ldap)
print("twa_ldap_str", twa_ldap_str)
# File name for the log
log_file_name = 'log-ldap-mod-des' + time_now.strftime('-%Y%m%d-%H%M%S') + '.txt'
path = Path.home()
full_log_filename = path / log_file_name
ff_log_file = open(full_log_filename, 'w')

# Description to be added to existing description, time stamp on description, Month and Year.
des_stamp = "Science IT Disabled " + time_now.strftime('%b %Y')

# Reading configuration, ldapq.ini
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
    query = '(&(objectcategory=computer)(!(UserAccountControl:1.2.840.113556.1.4.803:=2))(lastLogonTimestamp<=' + twa_ldap_str + '))'
    comp_list = find_generic(ad_ou, connection, query)

    # Dictionary holder of current computer attributes, to be changed ("description", "userAccountControl")
    # name is unique will be the key, containing a list of 4
    #      ["comp_name"] = [[0],             [1],               [2],                 [3]
    # note: "name", "distinguishedName", "description", "userAccountControl", "lastLogonTimestamp"
    dic_comp_cur_det = {}
    print('det_list len ', len(comp_list))
    ln_comp_num = 'det_list len ' + str(len(comp_list)) + ' computers to be disabled' + '\n' + \
                  'Line 1 current values: comp_dis_name UserAccountControl description LastLogonTimeStamp' + '\n' + \
                  'Line 2 proposed change: comp_dis_name UserAccountControl New_description' + '\n' + \
                  'Line 3: results of ldap modify, should include "success"' + '\n'

    ff_log_file.writelines([ln_comp_num])

    for i in comp_list:
        name = ""
        dist_name = ""
        existing_des = ""
        existing_uac = ""
        ts = ""

        if isinstance(i, list):

            for j in i:
                if j.header == 'name':
                    name = j.content[0]
                if j.header == 'distinguishedName':
                    dist_name = j.content[0]
                if j.header == 'description':
                    existing_des = j.content[0]
                if j.header == 'userAccountControl':
                    existing_uac = j.content[0]
                if j.header == 'lastLogonTimestamp':
                    ts = j.content[0]

            print(name, ' ', ts, ' ', dist_name, ' ', existing_des, ' ', existing_uac)
            #                 key        [0]        [1]            [2]       [3]
            dic_comp_cur_det[name] = [dist_name, existing_des, existing_uac, ts]

    make_change = input("Go ahead make the change y/n: ")

    if make_change == "y":

        for key_name in sorted(dic_comp_cur_det.keys()):
            new_des = ""
            new_uac = ""

            # New Description
            if dic_comp_cur_det[key_name][1] == "":  # if description is empty
                new_des = des_stamp
            else:
                new_des = dic_comp_cur_det[key_name][1] + " " + des_stamp
            # New User Account Control. 2, Account Disabled
            new_uac = str(int(dic_comp_cur_det[key_name][2]) | 2)

            # Changing order. easier for visual review of log.
            line_current = dic_comp_cur_det[key_name][0] + " " + dic_comp_cur_det[key_name][2] + " " + \
                           dic_comp_cur_det[key_name][1] + " " + dic_comp_cur_det[key_name][3]
            print(line_current)
            # time.sleep(.5)  # line change not include on some, might need time to write.
            line_change = dic_comp_cur_det[key_name][0] + " " + new_uac + " " + new_des
            print(line_change)
            line_current += '\n'
            line_change += '\n'
            ff_log_file.writelines([line_current, line_change])

            #   change = {'description': [(MODIFY_REPLACE, [new_des])],
            #             'UserAccountControl': [(MODIFY_REPLACE, ['2'])]}
            # Modify the description (With a time stamp added) and the UserAccountControl to disable it
            change = {'description': [(MODIFY_REPLACE, [new_des])], 'UserAccountControl': [(MODIFY_REPLACE, [new_uac])]}

            # modify_replace(ldap_connection, distinguished_name, change, verbose=True)
            result = modify_replace(connection, dic_comp_cur_det[key_name][0], change, True)
            print(result)
            ln_result_txt = (str(result)) + '\n'
            ff_log_file.writelines([ln_result_txt])

    ff_log_file.close()

    ldap_disconnect()
