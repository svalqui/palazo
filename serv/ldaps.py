# notes
#


import sys
import getpass
import configparser
import pathlib
import datetime


class LdResponse(object):
    """
    Class holder for the response.
    """

    def __init__(self):
        self.header = ""
        self.content = []


def object_to_text(item):
    """
    :param item: item of the response
    :return:
    """

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


def attributes_to_class(attributes, fields=[], debug=False):  # Attributes is a Dict
    """
    Flatens the Dictionary returned by ldap3; index to header, sub-structures to

    :param attributes:
    :param fields:
    :param debug:
    :return:
    """
    attributes_list = []
    try:
        if len(fields) == 0:
            for key in sorted(attributes.keys()):
                base_class = LdResponse()
                base_class.header = key
                if isinstance(attributes[key], list):
                    # print(line)
                    member_list = []
                    for element in attributes[key]:
                        if isinstance(element, str):
                            line = element
                            # print(line)
                            member_list.append(line)
                        else:
                            line = object_to_text(element)
                            # print(line)
                            member_list.append(line)
                    base_class.content = member_list
                    attributes_list.append(base_class)
                    if debug:
                        print("ATTRIBUTES Adding list", base_class.header, base_class.content)
                        print(attributes_list[0].header, attributes_list[-1].header, len(attributes_list))
                        print()
                elif isinstance(attributes[key], str):
                    base_class.content = [attributes[key]]  # making it a list, all content to be list
                    attributes_list.append(base_class)
                    if debug:
                        print("ATTRIBUTES Adding str", base_class.header, base_class.content)
                        print(attributes_list[0].header, attributes_list[-1].header, len(attributes_list))
                else:
                    base_class.content = [object_to_text(attributes[key])]  # making it a list, all content to be list
                    attributes_list.append(base_class)
                    if debug:
                        print("ATTRIBUTES Adding else", base_class.header, base_class.content)
                        print(attributes_list[0].header, attributes_list[-1].header, len(attributes_list))

        else:
            for field in fields:
                base_class = LdResponse()
                if field in attributes.keys():
                    base_class.header = field
                    if isinstance(attributes[field], list):
                        member_list=[]
                        for element in attributes[field]:
                            if isinstance(element, str):
                                member_list.append(element)
                            else:
                                line = object_to_text(element)
                                # print(line)
                                member_list.append(line)
                        base_class.content = member_list
                    elif isinstance(attributes[field], str):
                        base_class.content = [attributes[field]]  # making it a list, all content to be list
                    else:
                        base_class.content = [object_to_text(attributes[field])]  # making it a list,all content to list
                    attributes_list.append(base_class)
                else:
                    base_class.header = field
                    base_class.content = [""]
                    attributes_list.append(base_class)

    except BaseException as attribute_error:
        base_class = LdResponse()
        base_class.header = 'ERROR - LDAPAttributeError: ' + str(attribute_error) + ' Exception Name :' \
                            + str(type(attribute_error))
        base_class.content = [" "]
        if debug:
            print(base_class.header)
        attributes_list.append(base_class)

    return attributes_list  # list of Class LdResponse, LdResponse.content always a list


def attributes_to_list(attributes, fields=[]):  # Attributes is a Dict
    """
    :param attributes: a Dictionary from ldap3.connection.response
    :param fields: list of field to be included in the return is non all fields would be included.
    :return:
    """
    attributes_list = []
    try:
        if len(fields) == 0:
            for key in sorted(attributes.keys()):
                if isinstance(attributes[key], list):
                    line = key + " :"
                    # print(line)
                    attributes_list.append(line)
                    for element in attributes[key]:
                        if isinstance(element, str):
                            line = "   " + element
                            # print(line)
                            attributes_list.append(line)
                        else:
                            line = "   " + object_to_text(element)
                            # print(line)
                            attributes_list.append(line)
                elif isinstance(attributes[key], str):
                    line = key + " : " + attributes[key]
                    # print(line)
                    attributes_list.append(line)
                else:
                    line = key + " : " + object_to_text(attributes[key])
                    # print(line)
                    attributes_list.append(line)

        else:
            for field in fields:
                if field in attributes.keys():
                    if isinstance(attributes[field], list):
                        line = field + " :"
                        # print(line)
                        attributes_list.append(line)
                        for element in attributes[field]:
                            if isinstance(element, str):
                                line = "   " + element
                                # print(line)
                                attributes_list.append(line)
                            else:
                                line = "   " + object_to_text(element)
                                # print(line)
                                attributes_list.append(line)
                    elif isinstance(attributes[field], str):
                        line = field + " : " + attributes[field]
                        # print(line)
                        attributes_list.append(line)
                    else:
                        line = field + " : " + object_to_text(attributes[field])
                        # print(line)
                        attributes_list.append(line)

    except BaseException as attribute_error:
        line = 'ERROR - LDAPAttributeError: ' + str(attribute_error) + ' Exception Name :' + str(type(attribute_error))
        attributes_list.append(line)

    return attributes_list


def response_to_list(response, fields=[], debug=False):  # Connection.response, one to many entries
    response_list = []
    try:
        for index, one_response in enumerate(response):
            if 'attributes' in one_response.keys():
                attributes = attributes_to_list(one_response['attributes'], fields)
                response_list.append(attributes)
            else:
                if debug:
                    print("$$$$$$$$->", index + 1, " of ", len(response), " Response without attributes")

    except BaseException as response_error:
        line = 'ERROR - LDAPResponseListError: ' + str(response_error) + ' Exception Name :' + str(type(response_error))
        response_list.append(line)

    return response_list  # List of list, one list per entry


def response_to_list_class(response, fields=[], debug=False):
    response_list = []

    try:
        for index, one_response in enumerate(response):
            if 'attributes' in one_response.keys():
                attributes = attributes_to_class(one_response['attributes'], fields)
                response_list.append(attributes)
            else:
                if debug:
                    print("$$$$$$$$->", index + 1, " of ", len(response), " Response without attributes")

    except BaseException as response_error:
        base_class = LdResponse()
        base_class.header = 'ERROR - LDAPResponseListClassError: ' + str(response_error) + ' Exception Name :' \
                            + str(type(response_error))
        base_class.content = [" "]  # making it a list, all content to be list
        response_list.append(base_class)

    return response_list  # List of list of class LdResponse


def ldap_search(uri, base, user_name, user_password, query, debug=False):
    """
    ldap search
    :param uri:
    :param base:
    :param user_name:
    :param user_password:
    :param query:
    :param debug:
    :return:

    """
    from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES

    search_response = []  # list of dictionaries from ldap3
    line_error = ''

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

        search_response = conn.response

    except BaseException as search_error:
        line_error = 'ERROR - LDAPSearchError: ' + str(search_error) + ' Exception Name :' + str(type(search_error))
        if debug:
            print(line_error)

    return search_response, line_error


def find_domains(uri, base, user_name, user_password, domains=[], debug=False):  # for domains with sub-domains
    #   needs catch exceptions
    query = '(&(objectclass=domain)(dc=*))'
    q_response, line_error = ldap_search(uri, base, user_name, user_password, query)
    if debug:
        print(len(q_response))
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
                                find_domains(uri, ref, user_name, user_password, domains)

    return domains, line_error


def find_users(uri, base, user_name, user_password, look_for):
    query = '(&(objectClass=user)(objectCategory=person)(|(cn=*' + look_for + '*)(displayName=*' + look_for + '*)))'
    response, line_error = ldap_search(uri, base, user_name, user_password, query)
    return response_to_list_class(response)  # List of list of class Ld


def find_computers(uri, base, user_name, user_password, look_for, fields=[]):
    query = '(&(objectcategory=computer)(|(description=*' + look_for + '*)(name=*' + look_for + '*)))'
    response, line_error = ldap_search(uri, base, user_name, user_password, query)
    return response_to_list_class(response, fields)  # List of list, one list per entry


def find_groups(uri, base, user_name, user_password, look_for):
    query = '(&(objectclass=group)(name=*' + look_for + '*))'
    response, line_error = ldap_search(uri, base, user_name, user_password, query)
    return response_to_list_class(response)  # List of list, one list per entry


def main():

    # ldap_search(URI, BASE, QUERY)

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
    user_password = getpass.getpass()

    domains, line_error = find_domains(URI, BASE, user_name, user_password)
    print()
    print("Domains: ", domains)
    print("Error: ", line_error)
    print()
    for base in domains:
        print(">>>-------------->DOMAIN BASE : ", base, domains)
        l = find_users(URI, base, user_name, user_password, look_for)
        print("SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS ------       search concluded... printing ", len(l))
        for i in l:
            if isinstance(i, list):
                for j in i:
                    print(j.header, j.content)
                print()
            else:
                print(i)
                print(i.header, i.content)


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