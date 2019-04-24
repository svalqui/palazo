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


def q_os_release(urlpuppet, cacert, cert):
    q = {'query': ["=", "name", "operatingsystemrelease"]}
    print("q -->>>  ", q.__str__())
    script = json.dumps(q)  # takes an object, produces a string

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, q_os_release :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


def q_admin_users(urlpuppet, cacert, cert):
    print("on 1st")
    print(urlpuppet)
    print(cacert)
    print(cert)
    q = {'query': ["=", "name", "admin_user"]}
    print("q -->>>  ", q.__str__())
    script = json.dumps(q)  # takes an object, produces a string

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, first_q :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


def print_return(returned_json, fact_name):
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


def first_q(urlpuppet, cacert, cert):
    print("on 1st")
    print(urlpuppet)
    print(cacert)
    print(cert)
    #  --data-urlencode 'query=["=", "name", "operatingsystem"]'
#    q = {'query': ["=", "name", "operatingsystem"]}
    q = {'query': ["=", "name", "admin_user"]}
    print("q -->>>  ", q.__str__())
    script = json.dumps(q)  # takes an object, produces a string

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, first_q :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


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

        print('urlpuppet :', urlpuppet)
        print('cacert "', cacert)
        print('cert :', cert)

        my_query = input("[1] OS release \n "
                         "[2] Admin Users \n \n"
                         "Your Choice: ")

        if my_query == "1":
            fact_name = "operatingsystemrelease"
            r_jsn = q_os_release(urlpuppet, cacert, cert)
        elif my_query == "2":
            fact_name = "admin_user"
            r_jsn = q_admin_users(urlpuppet, cacert, cert)
        else:
            print("Wrong Choice.")

        print(str(type(r_jsn)))
        print_return(r_jsn, fact_name)

    except BaseException as e:
        print("Didn't work!, MAIN :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))


if __name__ == '__main__':
    sys.exit(main())
