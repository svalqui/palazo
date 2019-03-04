import requests
import json
import pathlib
import configparser

urlpuppet = "https://puppet.mysite.com:8081/pdb/query/v4/facts"
cacert = "/etc/puppetlabs/puppet/ssl/certs/ca.pem"

sslcert = "/etc/puppetlabs/puppet/ssl/certs/pc.pem"
sslkey = "/etc/puppetlabs/puppet/ssl/private_keys/pc.pem"
cert = (sslcert, sslkey)

q = {'query': ["=", "name", "operatingsystem"]}
script = json.dumps(q)

r = requests.get(urlpuppet, verify=cacert, cert=cert, data=script)
print(r.text)


def main():
    """ CLI implementation temporal for fast trial while developing
    it, requires puppetapi.ini 2 directories up with configuration as follow
    --- puppetapi.ini ---
    [Settings]
    url = https://puppet.mysite.com:8081/pdb/query/v4/facts
    cacert = /etc/puppetlabs/puppet/ssl/certs/ca.pem
    sslcert = /etc/puppetlabs/puppet/ssl/certs/pc.pem
    sslkey = /etc/puppetlabs/puppet/ssl/private_keys/pc.pem
    --- end of puppetapi.ini ---
    :return:
    """
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'puppetapi.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()

    try:
        config.read(str(file_conf_name))
