import ipaddress
import sys
from os import path
from tenable.io import TenableIO

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from ostack.tool import server_by_ip
import openstack

def main():
    tio_access_key = input("TIO_ACCESS_KEY: ")
    tio_secret_key = input("TIO_SECRET_KEY: ")
    cidr = input("CIDR: ")

    # Latest module
    os_conn = openstack.connect(cloud='envvars')

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
    # results = tio.exports.vulns(severity=["critical", ], cidr_range=cidr)
    results = tio.exports.vulns(severity=["critical","high", ], cidr_range=cidr)
    # results = tio.exports.vulns(plugin_id=[201456, 201420, 201351], cidr_range=cidr)

    my_pids = {}
    sorted_by_pid = {}

    for r in results:
#        if 'fqdn' in r['asset'].keys():
#            print('fqdn: ', r['asset']['fqdn'])
#        print('hostname: ', r['asset']['hostname'])
#        print('ipv4: ', r['asset']['ipv4'])
#        print('last_scan: ', r['asset']['last_scan_target'])
#        print('port: ', r['port'])
#        print('plugin name: ', r['plugin']['name'])
#        print('plugin id: ', r['plugin']['bid'])
#        print('state: ', r['state'])
##        print(r)
#        server_by_ip(r['asset']['last_scan_target'],os_conn)
#        print("-----------------")
#        print()
        if r['plugin']['bid'][0] in my_pids:
            my_pids[r['plugin']['bid'][0]][0] += 1
        else:
            my_pids[r['plugin']['bid'][0]] = [1, r['plugin']['name'], r['asset']['last_scan_target'], r['state'], r['port'] ]

        if r['plugin']['bid'][0] in sorted_by_pid.keys():
            # print(r['plugin']['bid'][0], " in keys")
            sorted_by_pid[r['plugin']['bid'][0]].append(r)
            # print("  length", len(sorted_by_pid[r['plugin']['bid'][0]]))
        else:
            # print(r['plugin']['bid'][0], " NOT in keys")
            sorted_by_pid[r['plugin']['bid'][0]] = [r]

    print("====")

    for id in sorted_by_pid.keys():
        p_1 = True
        for r in sorted_by_pid[id]:
            if p_1:
                print("-*-*-*-*-*-")
                print(r['plugin']['bid'][0], r['plugin']['name'])
                p_1 = False
            print(r['asset']['ipv4'], r['asset']['last_scan_target'], r['state'], r['port'])
            # server_by_ip(r['asset']['last_scan_target'], os_conn)
        print()


    print("====")

    print("ten_id, occurrences, ten_name, example_host, state, port")
    for k in my_pids.keys():
        print(k,
              ",",
              my_pids[k][0],
              ",",
              my_pids[k][1],
              ",",
              my_pids[k][2],
              ",",
              my_pids[k][3],
              ",",
              my_pids[k][4],
              )


if __name__ == '__main__':
    sys.exit(main())

