# notes
#
# looking for emails.
# ldapsearch -x -h domain.org -D "user@domain.org" -W -b "ou=an-ou,dc=domain, dc=org" -s sub "(cn=*)" cn mail sn

import sys
import getpass
import configparser
import pathlib
import datetime
from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

# Removing configuration from Project, configuration file 'ldapq.ini' moved 2 directories up
file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
print('file_conf_dir', file_conf_dir)
file_conf_name = pathlib.Path(file_conf_dir) / 'ldapq.ini'
print('file_conf_name', file_conf_name)

# Reading configuration
config = configparser.ConfigParser()

domains = []  # List of Domains and sub-domains

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

user_password = getpass.getpass()


def object_to_text(item):

    try:
        if isinstance(item, datetime.datetime):
            text = item.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(item, int):
            text = str(item)
        elif isinstance(item, bytes):
            text = str(item)
        else:
            text = str(item) + " is instance of : " + str(item.__class__) + " needs to be added to object_to_text"

    except BaseException as objtext_error:
        text = 'ERROR - LDAPObjTextError: ' + str(objtext_error) + ' Exception Name :' + str(type(objtext_error))

    return text


def get_attributes(attributes, fields=[]):  # Attributes is a Dict
    attributes_list = []

    try:
        if len(fields) == 0:
            for key in sorted(attributes.keys()):
                if isinstance(attributes[key], list):
                    line = key + " :"
                    print(line)
                    attributes_list.append(line)
                    for element in attributes[key]:
                        if isinstance(element, str):
                            line = "   " + element
                            print(line)
                            attributes_list.append(line)
                        else:
                            line = "   " + object_to_text(element)
                            print(line)
                            attributes_list.append(line)
                elif isinstance(attributes[key], str):
                    line = key + " : " + attributes[key]
                    print(line)
                    attributes_list.append(line)
                else:
                    line = key + " : " + object_to_text(attributes[key])
                    print(line)
                    attributes_list.append(line)

        else:
            for field in fields:
                if field in attributes.keys():
                    if isinstance(attributes[field], list):
                        line = field + " :"
                        print(line)
                        attributes_list.append(line)
                        for element in attributes[field]:
                            if isinstance(element, str):
                                line = "   " + element
                                print(line)
                                attributes_list.append(line)
                            else:
                                line = "   " + object_to_text(element)
                                print(line)
                                attributes_list.append(line)
                    elif isinstance(attributes[field], str):
                        line = field + " : " + attributes[field]
                        print(line)
                        attributes_list.append(line)
                    else:
                        line = field + " : " + object_to_text(attributes[field])
                        print(line)
                        attributes_list.append(line)

    except BaseException as attribute_error:
        line = 'ERROR - LDAPAttributeError: ' + str(attribute_error) + ' Exception Name :' + str(type(attribute_error))
        attributes_list.append(line)

    return attributes_list


def response_to_list(response, fields, debug=False):  # Connection.response
    response_list = []
    attributes = []
    try:
        for index, one_response in enumerate(response):
            if 'attributes' in response.keys():
                attributes = get_attributes(one_response['attributes'], fields)
            else:
                if debug:
                    print("$$$$$$$$->", index + 1, " of ", len(response), " Response without attributes")
            response_list += attributes
    except BaseException as response_error:
        line = 'ERROR - LDAPResponseError: ' + str(response_error) + ' Exception Name :' + str(type(response_error))
        response_list += line

    return response_list


def ldap_search(uri, base, query, fields=[], debug=False):
    '''
    ldap search
    :param uri:
    :param base:
    :param query:
    :param fields:
    :param debug:
    :return:
    '''

    search_response = []

    if debug:
        print()
        print('URI :', uri)
        print('BASE :', base)
        print('QUERY :', query)

    try:
        server = Server(uri, use_ssl=True, get_info=ALL)
        conn = Connection(server, user=user_name, password=user_password, auto_bind=True)
        # conn = Connection(server, auto_bind=True, authentication=SASL, sasl_mechanism='GSSAPI')
        conn.search(base, query, attributes=ALL_ATTRIBUTES)
        if debug:
            print(" RESPONSE LENGTH ", len(conn.response), " ENTRIES LENGTH ", len(conn.entries))
            # print()
        search_response = response_to_list(conn.response, fields)

    except BaseException as search_error:
        line = 'ERROR - LDAPSearchError: ' + str(search_error) + ' Exception Name :' + str(type(search_error))
        search_response += line

    return search_response


def find_domains(uri, base, debug=False):  # for domains with sub-domains

    query = '(&(objectclass=domain)(dc=*))'
    q_response = ldap_search(uri, base, query, ['dc', 'distinguishedName', 'subRefs'])
    if len(q_response) > 0:
        for one_response in q_response:
            if 'attributes' in one_response.keys():

                if one_response['attributes']['distinguishedName'].find('DomainDnsZones') < 0 and \
                                one_response['attributes']['distinguishedName'].find('ForestDnsZones') < 0:
                    if one_response['attributes']['distinguishedName'] not in domains:

                        domains.append(one_response['attributes']['distinguishedName'])
                        if debug:
                            print('+++ Adding Domain :', one_response['attributes']['distinguishedName'])
                    if 'subRefs' in one_response['attributes'].keys():
                        if len(one_response['attributes']['subRefs']) > 0:
                            for ref in one_response['attributes']['subRefs']:
                                # print("ref -> ", ref)
                                find_domains(uri, ref)
    return domains


def find_users(uri, base):
    query = '(&(objectClass=user)(objectCategory=person)(|(cn=*' + look_for + '*)(displayName=*' + look_for + '*)))'
    return ldap_search(uri, base, query)


def find_computers(uri, base):
    query = '(&(objectcategory=computer)(|(description=*' + look_for + '*)(name=*' + look_for + '*)))'
    return ldap_search(uri, base, query)


def find_groups(uri, base):
    query = '(&(objectclass=group)(name=*' + look_for + '*))'
    return ldap_search(uri, base, query)


def main():
    # ldap_search(URI, BASE, QUERY)
    find_domains(URI, BASE)
    print()
    for base in domains:
        print(">>>-------------->DOMAIN BASE : ", base, domains)
        find_users(URI, base)


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
# https://social.technet.microsoft.com/Forums/scriptcenter/en-US/191a7f47-d4a7-4e06-af78-e9d2699a464a/get-all-sub-domains?forum=ITCG
# https://stackoverflow.com/questions/1400933/active-directory-search-for-only-user-objects