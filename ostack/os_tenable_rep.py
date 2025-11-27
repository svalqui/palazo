
# https://pytenable.readthedocs.io/en/stable/api/io/exports.html

import ipaddress
import os
import sys
from os import path

import arrow
from tenable.io import TenableIO

from prettytable import PrettyTable
import openstack


sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def render_table(my_dict, columns, my_title, sortby):
    table = PrettyTable()
    if my_title != "":
        table.title = my_title
    table.field_names = columns
    table.align = 'l'
    my_row=[]
    for prj_id in my_dict.keys():
        # row, a list matching the number of elements of the table's fields
        for vm_ip in my_dict[prj_id]:
            for plug in my_dict[prj_id][vm_ip]:
                my_row = [prj_id, vm_ip] + plug
                table.add_row(my_row)
    if sortby:
        table.sortby = sortby
    print(table)
    return table


def get_instance_by_ip(svr_ip, os_conn):
    my_ports = os_conn.list_ports(filters={'fixed_ips': ['ip_address=' + svr_ip]})
    # print("port device_id: ", my_ports[0].device_id)
    # print("port project_id: ", my_ports[0].project_id)
    return os_conn.get_server_by_id(my_ports[0].device_id)

def get_prj_id_by_ip(svr_ip, os_conn):
    my_ports = os_conn.list_ports(filters={'fixed_ips': ['ip_address=' + svr_ip]})
    return my_ports[0].project_id


def main():
    cidr = input("CIDR: ")

    os_conn = openstack.connect(cloud='envvars')
    # os_conn.get_floating_ip()
    # os_conn.list_floating_ips()
    # os_conn.server

    tio_access_key = os.getenv("TIO_ACCESS_KEY")
    tio_secret_key = os.getenv("TIO_SECRET_KEY")

    tio = TenableIO(
        tio_access_key,
        tio_secret_key,
    )

    cidr_obj = ipaddress.ip_network(cidr)

    results = tio.exports.vulns(severity=["critical","high", "medium", ], cidr_range=cidr)
    my_assets = tio.exports.assets(updated_at=int(arrow.now().shift(days=-7).timestamp()))

    by_prj_id = {}

    for r in results:
        # print('hostname: ', r['asset']['hostname'])
        # # print('ipv4: ', r['asset']['ipv4'])
        # print('last_scan: ', r['asset']['last_scan_target'])
        # print('plugin name: ', r['plugin']['name'])
        # print('plugin id: ', r['plugin']['bid'])
        # print('state: ', r['state'])
        # print('severity: ', r['severity'])
        # print('severity_id: ', r['severity_id'])
        # print('last_found: ', r['last_found'])
        # print()
        # # vm = get_instance_by_ip( r['asset']['last_scan_target'], os_conn)

        vm_prj_id = get_prj_id_by_ip(r['asset']['last_scan_target'], os_conn)

        my_row = [r['asset']['hostname'],
                  # r['asset']['last_scan_target'],
                  r['severity'],
                  r['severity_id'],
                  r['plugin']['bid'][0],
                  r['plugin']['name'],
                  r['state'],
                  r['last_found'],
                  ]


        if vm_prj_id in by_prj_id:
            if r['asset']['last_scan_target'] in by_prj_id[vm_prj_id]:
                by_prj_id[vm_prj_id][r['asset']['last_scan_target']].append(my_row)
            else:
                by_prj_id[vm_prj_id][r['asset']['last_scan_target']] = [my_row]
        else:
            by_prj_id[vm_prj_id] = {r['asset']['last_scan_target']: [my_row]}

    columns = [
        'prj_id',
        'vm_ip',
        'hostname',
        'severity',
        'severity_id',
        'plugin_id',
        'plugin_name',
        'state',
        'last_found',
    ]
    render_table(by_prj_id,columns, 'Vulnerabilities','prj_id')

    print()
    for a in my_assets:
        print(a)

    print()
    for k in my_assets[0]:
        print(k, my_assets[0][k])



if __name__ == '__main__':
    sys.exit(main())

