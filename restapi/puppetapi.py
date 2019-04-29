import requests
import json
import pathlib
import configparser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import restapi.restapimaster


class Jn(restapi.restapimaster.RestApi):
    def __init__(self, jsn):
        self.navigate_json(jsn)


def query_fact(urlpuppet, cacert, cert, fact_name):
    """ Returns.
    {
    "certname": <node name>,
    "name": <fact name>,
    "value": <fact value>,
    "environment": <facts environment>
    }
    """
    q = {'query': ["=", "name", fact_name]}
    print("q -->>>  ", q.__str__())
    script = json.dumps(q)  # takes an object, produces a string

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, q_os_release :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


def print_rec_by_fact_name(returned_json, fact_name):
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
                else:
                    print("Another fact named: ", record['name'])

    print("number of matching records: ", number_of_matching)


def print_test(returned_json, fact_name):
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

                else:
                    print("Another fact named: ", record['name'], "V :", record['value'])

    print("number of matching records: ", number_of_matching)



def main():
    """ CLI implementation temporal for fast trial while developing
    it, requires puppetapi.ini 3 directories up with configuration as follow
    --- puppetapi.ini ---
    [Settings]
    url = https://puppet.mysite.com:8081/pdb/query/v4/facts
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

        urlpuppet = config['Settings']['url']
        cacert = config['Settings']['cacert']
        sslcert = config['Settings']['sslcert']
        sslkey = config['Settings']['sslkey']
        cert = (sslcert, sslkey)

        my_query = input("[1] OS release \n "
                         "[2] Admin Users \n \n"
                         "Your Choice: ")

        if my_query == "1":
            fact_name = "operatingsystemrelease"
            r_jsn = query_fact(urlpuppet, cacert, cert, fact_name)
        elif my_query == "2":
            fact_name = "admin_user"
            r_jsn = query_fact(urlpuppet, cacert, cert, fact_name)
        else:
            print("Wrong Choice.")

        print(str(type(r_jsn)))
        print_rec_by_fact_name(r_jsn, fact_name)
        print('urlpuppet :', urlpuppet)
        print('cacert "', cacert)
        print('cert :', cert)




    except BaseException as e:
        print("Didn't work!, MAIN :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))


if __name__ == '__main__':
    sys.exit(main())
