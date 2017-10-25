# notes
#
# looking for emails.
# ldapsearch -x -h domain.org -D "user@domain.org" -W -b "ou=an-ou,dc=domain, dc=org" -s sub "(cn=*)" cn mail sn

import sys
import getpass
import configparser
import pathlib
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

# Removing configuration from Project, configuration file 'ldapq.ini' moved 2 directories up
file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Reading configuration
config = configparser.ConfigParser()

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

# Query
look_for = input("Search AD for :")
QUERY = '(|(cn=*' + look_for + '*)(&(objectcategory=computer)(name=*' + look_for + '*))(&(objectclass=group)(name=*' + look_for +'*)))'
# QUERY = '(cn=*val*)'
# QUERY = '(givenName=val*)'
# QUERY = '(&(objectcategory=computer)(name=*11611*))'
# (&(objectclass=group)(name=*116109*))

user_password = getpass.getpass()


def show_detail(detail): # List or Value
    if isinstance(detail, list):
        print(detail)
        for element in detail:
            print("   ", element)
    else:
        print(" -> ", detail)


def show_attributes(one_response, fields=[]):  # Attributes is a Dict

    attributes = one_response['attributes']

    if len(fields) == 0:
        for key in sorted(attributes.keys()):
            if isinstance(attributes[key], list):
                print(key)
                for element in attributes[key]:
                    print("   ", element)
            else:
                print(key, " -> ", attributes[key])

        print("-----End of above attribute")
        print()

    else:

        for field in fields:
            if field in attributes.keys():
                if isinstance(attributes[field], list):
                    print(field)
                    for element in attributes[field]:
                        print("   ", element)
                else:
                    print(field, " : ", attributes[field])


def show_response(one_response):  # response is a Dict
    if 'attributes' in one_response.keys():
        show_attributes(one_response)
        # show_attributes(one_response, show_fields)
    # else:
    #     print("NO ATTRIBUTES for this response ", one_response.__class__)
    #     print(one_response)


def ldap_search(uri, base, query):
    '''
    ldap search
    :param uri:
    :param base:
    :param query:
    :return:
    '''

    try:
        server = Server(uri, get_info=ALL)
        conn = Connection(server, user=user_name, password=user_password, auto_bind=True)
        print(conn)
#        print(server.schema)
        conn.search(base, query, attributes=ALL_ATTRIBUTES)
        print(" RESPONSE LENGTH ", len(conn.response), " ENTRIES LENGTH ", len(conn.entries))
        print()
        print("****---****")

        for index, one_response in enumerate(conn.response):
            print("---Response---", index)
            show_response(one_response)

    except BaseException as e:
        print('LDAPError: ', e)
        print('Exception Name :', type(e).__Name__)


def main():
    print('URI :', URI)
    print('BASE :', BASE)
    print('QUERY ;', QUERY)
    ldap_search(URI, BASE, QUERY)


if __name__ == '__main__':
    sys.exit(main())

# Credits Disclaimer
# The below sites/articles/code has been used totally, partially or as reference
#
#
# http://everythingisgray.com/2014/06/01/complex-ldap-queries-with-ldapsearch-and-python-ldap/
# https://stackoverflow.com/questions/13410540/how-to-read-the-contents-of-active-directory-using-python-ldap
# https://stackoverflow.com/questions/2193362/how-to-connect-to-a-ldap-server-using-a-p12-certificate
# https://stackoverflow.com/questions/4990718/python-about-catching-any-exception
# https://stackoverflow.com/questions/27844088/python-get-directory-two-levels-up
# https://wiki.python.org/moin/HandlingExceptions
# https://docs.python.org/3/library/pathlib.html
# https://docs.python.org/3/library/configparser.html
# http://ldap3.readthedocs.io/tutorial_intro.html
