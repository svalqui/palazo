import requests
import json
import pathlib
import configparser
import sys


print("on Puppet")


def first_q(urlpuppet, cacert, cert):
    print("on 1st")
    print(urlpuppet)
    print(cacert)
    print(cert)
    q = {'query': ["=", "name", "operatingsystem"]}
    print("q", q.__str__())
    script = json.dumps(q)

    try:
        r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)

    except BaseException as e:
        print("Didn't work!, first_q :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))

    print(r.text)


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

        first_q(urlpuppet, cacert, cert)

    except BaseException as e:
        print("Didn't work!, MAIN :(")
        print('--Error: ', e)
        print('--Exception Name :', type(e))


if __name__ == '__main__':
    sys.exit(main())
