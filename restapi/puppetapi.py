# Copyright 2019-2023 by Sergio Valqui. All rights reserved.
import requests
import pathlib
import configparser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import restapi.restapimaster
"""Tools to query PuppetDB.
    https://puppet.com/docs/puppetdb/4.1/api/query/v4/entities.html
"""


def query_a_fact(url_base, cacert, cert, fact_name):
    """Query a fact.

    Returns.
    json, list of dict.
    {
    "certname": <node name>,
    "name": <fact name>,
    "value": <fact value>,
    "environment": <facts environment>
    }
    """
    url_puppet = url_base + "/facts"

    q = {'query': '["=", "name", "'+fact_name+'"]'}
    print("q -->>>  ", q.__str__())

    try:
        r = requests.get(url_puppet, verify=cacert, cert=cert, data=q)
    except BaseException as e:
        print("Didn't work!, q_os_release :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


def query_inventory(url_base, cacert, cert):
    """Query a pre-defined list of facts, HW details and other as per list.

     Returns.
     json, lis of Dict
    {
    "certname": <node name>,
    "name": <fact name>,
    "value": <fact value>,
    "environment": <facts environment>
    }
    """
    url_puppet = url_base + "/facts"

    q = {'query': '["or",["=", "name", "manufacturer"],["=", "name", "boardassettag"],["=", "name", "memorysize"],'
                  '["=", "name", "memoryfree"],["=", "name", "lsbdistdescription"],["=", "name", "network"],'
                  '["=", "name", "last_login_date"],["=", "name", "admin_user"], ["=", "name", "productname"],'
                  ' ["=", "name", "operatingsystem"], ["=", "name", "operatingsystemrelease"], '
                  '["=", "name", "serialnumber"]]'}

    print("q -->>>  ", q.__str__())

    try:
        r = requests.get(url_puppet, verify=cacert, cert=cert, data=q)

    except BaseException as e:
        print("Didn't work!, q_os_release :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


def print_rec_by_fact_name(returned_json, fact_name):
    """Print Node and Fact value correspondent to the given fact name."""
    number_of_matching = 0

    for record in returned_json:
        if isinstance(record, dict):
            if 'name' in record.keys():
                if record['name'] == fact_name:
                    number_of_matching += 1
                    print("Node ", number_of_matching, " :", record['certname'])
                    print("Environment :", record['environment'])
                    print("Value :", record['value'])
                    print()

    print("number of matching records: ", number_of_matching)


def print_test(returned_json, fact_name):
    """Print as per coded, this is to test the printing format for different queries."""
    number_of_matching = 0

    for record in returned_json:
        if isinstance(record, dict):
            if 'name' in record.keys():
                if record['name'] == fact_name:
                    number_of_matching += 1
                    print("Node ", number_of_matching, " :", record['certname'])
                    print("Environment :", record['environment'])
                    print("Value :", record['value'])
                    print()
                elif record['name'] == 'bios_vendor':
                    print("Node :", record['certname'])
                    print("Environment :", record['environment'])
                    print("Value :", record['value'])
                    print()

    print("number of matching records: ", number_of_matching)


def print_dict_filtered(dict_filtered):
    for node_name in dict_filtered.keys():
        print('Node: ', node_name)
        for fact_name in dict_filtered[node_name].keys():
            print('    Fact: ', fact_name)
            print('    Value: ', dict_filtered[node_name][fact_name])


def print_dict_inventory(dict_filtered):
    line_facts = ''

    inventory_fields = ["operatingsystem", "operatingsystemrelease", "lsbdistdescription", "manufacturer",
                        "productname", "serialnumber", "boardassettag", "memorysize", "memoryfree", "last_login_date",
                        "network", "admin_user"]

    print('Node, OS, OS Release, OS Distrib, Manufacturer, Model, Serial Number, Asset Tag, Memory Size, Memory Free, '
          'Last Login Date, IP, User')
    for node_name in dict_filtered.keys():
        line_per_node = node_name
        for fact_name in inventory_fields:
            if fact_name in dict_filtered[node_name].keys():
                line_facts += ", " + str(dict_filtered[node_name][fact_name]).replace(',', ';')
            else:
                line_facts += ", "
        line_per_node += line_facts
        line_facts = ''

        print(line_per_node)


def json_facts_filtered(returned_json, filter_fields=['manufacturer', 'boardassettag', 'memorysize', 'memoryfree']):
    """Create a nested dict, nodes-to-facts, indexed by certname(node_name), sub-index fact_name.

    Creates the dict from the returned_json, Use filter_fields to only included the listed facts on the dict."""

    dict_filtered = {}  # Index per certname
    for record in returned_json:
        if isinstance(record, dict):
            if 'name' in record.keys():
                if record['name'] in filter_fields:
                    if record['certname'] in dict_filtered.keys():
                        dict_filtered[record['certname']][record['name']] = record['value']
                    else:
                        dict_filtered[record['certname']] = {}
                        dict_filtered[record['certname']][record['name']] = record['value']
    return dict_filtered


def json_facts_inventory(returned_json):
    """Create a nested dict, nodes-to-facts, indexed by certname(node_name), sub-index inventory_fields.

    Creates the dict from the returned_json, Use inventory_fields to only included those facts on the dict.."""

    inventory_fields = ["operatingsystem", "operatingsystemrelease", "lsbdistdescription", "manufacturer",
                        "productname", "serialnumber", "boardassettag", "memorysize", "memoryfree", "last_login_date",
                        "network", "admin_user"]
    return json_facts_filtered(returned_json, inventory_fields)


def main():
    """ CLI implementation temporal for fast trial while developing
    it, requires puppetapi.ini 3 directories up with configuration as follow
    --- puppetapi.ini ---
    [Settings]
    url = https://puppet.mysite.com:8081/pdb/query/v4
    cacert = /etc/puppetlabs/puppet/ssl/certs/ca.pem
    sslcert = /etc/puppetlabs/puppet/ssl/certs/pc.pem
    sslkey = /etc/puppetlabs/puppet/ssl/private_keys/pc.pem
    --- end of puppetapi.ini ---
    :return:
    """
    file_conf_dir = pathlib.Path(__file__).absolute().parents[3]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'puppetapi.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()

    try:
        config.read(str(file_conf_name))

        url_base = config['Settings']['url']
        cacert = config['Settings']['cacert']
        sslcert = config['Settings']['sslcert']
        sslkey = config['Settings']['sslkey']
        cert = (sslcert, sslkey)

        print('urlbase :', url_base)
        print('cacert "', cacert)
        print('cert :', cert)
        print()

        my_query = input("[1] OS release \n"
                         "[2] Admin Users \n"
                         "[3] HW Report \n \n"
                         "Your Choice: ")

        if my_query == "1":
            fact_name = "operatingsystemrelease"
            r_jsn = query_a_fact(url_base, cacert, cert, fact_name)
        elif my_query == "2":
            fact_name = "admin_user"
            r_jsn = query_a_fact(url_base, cacert, cert, fact_name)
        elif my_query == "3":
            r_jsn = query_inventory(url_base, cacert, cert)
            filtered_facts = json_facts_inventory(r_jsn)
            print_dict_inventory(filtered_facts)
        else:
            print("Wrong Choice.")

        print()
        print(str(type(r_jsn)))
        # print_test(r_jsn, fact_name)
        print('urlbase :', url_base)
        print('cacert "', cacert)
        print('cert :', cert)

    except BaseException as e:
        print("Didn't work!, MAIN :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))


if __name__ == '__main__':
    sys.exit(main())
