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
    print("on 1st")
    print(urlpuppet)
    print(cacert)
    print(cert)
    #  --data-urlencode 'query=["=", "name", "operatingsystem"]'
#    q = {'query': ["=", "name", "operatingsystem"]}
    q = {'query': ["=", "name", "operatingsystemrelease"]}
    print("q -->>>  ", q.__str__())
    script = json.dumps(q)  # takes an object, produces a string

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, first_q :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    return r.json()


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
        print("on try")

        r_jsn = first_q(urlpuppet, cacert, cert)
        #Jn(r_jsn)
        print(str(type(r_jsn)))
        n_d = 0
        # for i in r_jsn:
        #     if isinstance(i, dict):
        #         n_d += 1
        #         for j in i.keys():
        #             print(j, str(type(i[j])), ' ', i[j])
        #     else:
        #         print(str(type(i)))
        #     print()

        for i in r_jsn:
            if isinstance(i, dict):
                if 'name' in i.keys():

                    #if i['name'] == 'operatingsystemrelease':
                    if i['name'] == 'admin_user':
                        n_d += 1
                        print("Node ", n_d, " :", i['certname'])
                        print("Environment :", i['environment'])
                        print("OS Release :", i['value'])
                        print()




        print("n_d: ", n_d)

    except BaseException as e:
        print("Didn't work!, MAIN :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))


if __name__ == '__main__':
    sys.exit(main())
