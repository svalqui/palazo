#!/usr/bin/env python
import datetime

import os
import sys
from operator import itemgetter

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as ks_client

from collections import OrderedDict

import openstack

from os import path
import sys


sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def main():
    """ CLI implementation temporal for fast trial while developing
    """
    mmy_prj = input("Project_id: ")
    print(datetime.datetime.now(), "about to connect...", )
    os_conn = openstack.connect(cloud='envvars')

    print(datetime.datetime.now(), "connected looking for servers...", )
    servers = os_conn.list_servers(all_projects=True, filters={'project_id': my_prj})

    prj_flavors = {}  # flavor, number of VMs
    rdw = 0
    rdl = 0
    rsw = 0
    rsl = 0
    rssl = 0
    other_VMs = 0

    total_vcpus = 0
    total_ram = 0

    cpu_genoa = 0
    cpu_milan = 0
    cpu_gpu = 0
    cpu_bigmem = 0
    cpu_other = 0

    for s in servers:
        # print(s.name, s.flavor, s.flavor_id, s.vm_state)

        if len(s.name) > 5:
            if s.name[:5] == 'rd-w-':
                rdw += 1
            elif s.name[:4] == 'rdw-':
                rdw += 1
            elif s.name[:5] == 'rd-l-':
                rdl += 1
            elif s.name[:4] == 'rdl-':
                rdl += 1
            elif s.name[:5] == 'rs-w-':
                rsw += 1
            elif s.name[:5] == 'rs-l-':
                rsl += 1
            elif s.name[:5] == 'rss-l':
                rssl += 1
            else:
                other_VMs += 1
        else:
            other_VMs += 1

        total_vcpus += s.flavor.vcpus
        total_ram += s.flavor.ram

        if s.flavor.original_name in prj_flavors:
            prj_flavors[s.flavor.original_name] += 1
        else:
            prj_flavors[s.flavor.original_name] = 1

        if "uom.general" in s.flavor.original_name:
            if ".v3" in s.flavor.original_name:
                cpu_genoa += s.flavor.vcpus
            else:
                cpu_milan += s.flavor.vcpus
        elif "uom.rcp.bigmem" in s.flavor.original_name:
            cpu_bigmem += s.flavor.vcpus
        elif "uom.vgpu." in s.flavor.original_name:
            cpu_gpu += s.flavor.vcpus
        else:
            cpu_other += s.flavor.vcpus

    print(datetime.datetime.now(), "Counting distributions...", )
    print(len(servers))

    print("rdw VMs:", rdw)
    print("rdl VMs:", rdl)
    print("rsw VMs:", rsw)
    print("rsl VMs:", rsl)
    print("rsslVMs:", rssl)
    print("Other VMs:", other_VMs)
    print("Total VMs ", rdw + rdl + rsw + rsl + rssl + other_VMs)

    print("Total VCPUs", total_vcpus)
    print("Total RAM", total_ram)

    print()
    print("CPUs used on Milan", cpu_milan)
    print("CPUs used on Genoa", cpu_genoa)
    print("CPUs used on GPU", cpu_gpu)
    print("CPUs used on BigMem", cpu_bigmem)
    print("CPUs used on Other", cpu_other)
    print("CPUs used Total", cpu_milan + cpu_genoa + cpu_gpu + cpu_bigmem + cpu_other)

    print()
    print("Break out of VMs per flavor")

    flavor_sorted = OrderedDict(sorted(prj_flavors.items(), key=itemgetter(1)))

    for i, v in flavor_sorted.items():
        print (i, v)


if __name__ == '__main__':
    sys.exit(main())
