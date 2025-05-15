import ipaddress
import sys
from tenable.io import TenableIO

def main():
    tio_access_key = input("TIO_ACCESS_KEY: ")
    tio_secret_key = input("TIO_SECRET_KEY: ")
    cidr = input("CIDR: ")

    tenable_vendor = ""
    tenable_product = ""
    tenable_version = ""

    tio = TenableIO(
        tio_access_key,
        tio_secret_key,
        vendor=tenable_vendor,
        product=tenable_product,
        build=tenable_version,
    )

    cidr_obj = ipaddress.ip_network(cidr)

    print(cidr_obj)

#    results = tio.exports.vulns(plugin_id=plugin_ids, cidr_range=config.TARGET_CIDR)
    # https://pytenable.readthedocs.io/en/1.4.7/api/io/exports.html
    # results = tio.exports.vulns(plugin_id=[149334,], cidr_range=cidr)
    results = tio.exports.vulns(severity=["critical", ], cidr_range=cidr)

    for r in results:
        if 'fqdn' in r['asset'].keys():
            print('fqdn: ', r['asset']['fqdn'])
        print('hostname: ', r['asset']['hostname'])
        print('ipv4: ', r['asset']['ipv4'])
        print('last_scan: ', r['asset']['last_scan_target'])
        print('port: ', r['port'])
        print('plugin name: ', r['plugin']['name'])
        print('plugin id: ', r['plugin']['bid'])
        print(r)
        print("-----------------")
        print()


if __name__ == '__main__':
    sys.exit(main())

