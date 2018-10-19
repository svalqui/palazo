#
# Delete computer accounts that match a given string, are older than a year and have been disabled()
#
# export PYTHONPATH=`pwd`

from serv.ldaps import ldap_connect, find_generic, ldap_delete
from pathlib import Path
import datetime
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
    look_for = input("Search AD for computer accounts containing :")
    user_password = getpass.getpass()

    time_now = datetime.datetime.now()
    year = datetime.timedelta(days=365)
    year_ago = time_now - year
    # a year ago on ldap format
    year_ago_ldap = year_ago.strftime("%Y%m%d%H%M%S") + ".0Z"

    # query for computer accounts look_for, without members, that are disabled and NOT been changed during last year
    query = '(&(objectcategory=computer)(userAccountControl=4130)' \
            '(|(description=*' + look_for + '*)(name=*' + look_for + '*))(whenChanged<=' + year_ago_ldap + '))'

    connection = ldap_connect(URI, user_name, user_password)

    list_detailed = find_generic(BASE, connection, query)
    list_report = find_generic(BASE, connection, query, ["name", "operatingSystem", "operatingSystemVersion",
                                                         "lastLogonTimestamp", "distinguishedName", "description",
                                                         "userAccountControl"])
    list_length = len(list_report)

    filename = 'ldap_delete_comp_acc-' + time_now.strftime('-%Y%m%d-%H%M%S') + '_detailed.txt'
    path = Path.home()
    fs_filename = path / filename
    ff_file_detailed = open(fs_filename, 'w')

    # saving detailed list, object details that are going to be deleted
    for index, entry in enumerate(list_detailed):
        ff_file_detailed.write('Record ' + str(index + 1) + ' of ' + str(list_length) + '\n')
        for rec in entry:
            ff_file_detailed.write(str(rec.header) + str(rec.content) + '\n')
        ff_file_detailed.write('\n')
    ff_file_detailed.close()

    # shows a summary list of computer accounts that are going to be deleted
    for index, i in enumerate(list_report):
        my_row = []
        for j in i:
            if len(j.content) == 1:
                value = j.content[0]
            else:
                value = "Multiple Values"
            my_row.append(value)
        print("\t".join(my_row))

    print("\nTotal :", list_length)

    sure_to_delete = input("Are you sure you want to delete the listed accounts? (y)")

    if sure_to_delete == 'y':
        filename = 'ldap_delete_comp_acc-' + time_now.strftime('-%Y%m%d-%H%M%S') + '_deleted.txt'
        path = Path.home()
        fs_filename = path / filename
        ff_file_deleted = open(fs_filename, 'w')
        records_deleted = 0

        for entry in list_report:
            for rec in entry:
                if rec.header == 'distinguishedName':
                    print(rec.content[0])
                    ldap_delete(connection, rec.content[0], True)
                    ff_file_deleted.write(rec.content[0] + '\n')
                    ff_file_deleted.write(str(connection.result) + '\n')
                    if 'description' in connection.result.keys():
                        if connection.result['description'] == 'success':
                            records_deleted += 1
                    ff_file_deleted.write('Total Records deleted :' + str(records_deleted) + '\n')

        print("\nTotal records deleted :", records_deleted)
        ff_file_deleted.close()

# Credits Disclaimer
# The below sites/articles/code has been used totally, partially or as reference
# https://morgansimonsen.com/2008/08/12/how-to-use-the-whencreated-and-whenchanged-attributes-to-search-for-objects-in-active-directory/
# https://stackoverflow.com/questions/4028904/how-to-get-the-home-directory-in-python
#