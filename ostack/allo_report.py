#!/usr/bin/env python
import datetime

import os
import sys
from operator import itemgetter

import openstack
from fontTools.misc.plistlib import end_date
from oauthlib.uri_validate import query

from openstack.block_storage.v3 import volume
from keystoneauth1.identity import v3
from keystoneauth1 import session

from nectarallocationclient import client as allo_client

from os import path
import sys

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def os_auth_env_sess():
    """Authenticates using keystone, using environmental variables. returns a session"""
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       username=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'],
                       user_domain_id='default')
    os_session = session.Session(auth=auth)

    return os_session

def server_resources(l_servers, resources):
    print(datetime.datetime.now(), "Resources of servers... ")
    resources['instances'] = 0
    resources['vcpus'] = 0
    resources['ram'] = 0
    for s in l_servers:
        resources['instances'] += 1
        # print("   server status", s.status,)
        if s.status != 'SHELVED_OFFLOADED':
            resources['vcpus'] += s.flavor.vcpus
            resources['ram'] += s.flavor.ram
    return resources

def volume_resources(g_volumes, resources):
    print(datetime.datetime.now(), "Resources of volumes... ")
    resources['gigabytes'] = 0
    for v in g_volumes:
        resources['gigabytes'] += v.size
    return resources

def project_resources(os_conn, project_id):
    p_resources= {}
    print(datetime.datetime.now(), "Getting Servers for project ", project_id)
    p_servers = os_conn.list_servers(all_projects=True, filters={'project_id':project_id}) #  List of server_obj
    print(datetime.datetime.now(), "Servers", len(p_servers))
    p_resources = server_resources(p_servers, p_resources)

    print(datetime.datetime.now(), "Getting volumes for project ", project_id)
    p_volumes = os_conn.block_storage.volumes(all_projects=True, project_id=project_id) # Generator
    p_resources = volume_resources(p_volumes, p_resources)

    p_com_quo = os_conn.get_compute_quotas(project_id)
    # print("Quota Instances", p_com_quo.instances)
    # print("Quota Cores", p_com_quo.cores)
    # print("Quota Ram", p_com_quo.ram)
    p_resources['quota_instances'] = p_com_quo.instances
    p_resources['quota_cores'] = p_com_quo.cores
    p_resources['quota_ram'] = p_com_quo.ram

    p_vol_quo = os_conn.get_volume_quotas(project_id)
    # print("Quota Vol Storage", p_vol_quo.gigabytes)
    p_resources['quota_gigabytes'] = p_vol_quo.gigabytes
    # print(p_resources)

    return p_resources

def top_ones (top_number, resources, index, p_id, p_name, l_top):
    if len(l_top) > top_number - 1 :
        if resources[index] > l_top[4][0]:
            l_top = l_top[:-1]
            l_top.append((resources[index], p_id, p_name))
            l_top.sort(reverse=True)
    else:
        l_top.append((resources[index], p_id, p_name))
        l_top.sort(reverse=True)
    return l_top


def main():
    """ fast trial of alloc report
    """

    # Session for allocations
    my_session = os_auth_env_sess()

    # os_connection for nova and cinder
    os_conn = openstack.connect(cloud='envvars')

    # clients
    allo_cli = allo_client.Client(version=1, session=my_session)

    ## Allocation report all active
    print(datetime.datetime.now(), "Getting Allocations")
    allocations_active = allo_cli.allocations.list(associated_site='uom',
                                                   status='A',
                                                   provisioned=True,
                                                   parent_request=None,
                                            )
    print(datetime.datetime.now(), "Allocations ", len(allocations_active))

    # index allocations by allocation id
    #allocations_dict = {}
    #for allocation in allocations_active:
    #    allocations_dict[allocation.id] = allocation

    # hide = ["Deleted", "Approved"]

    my_today = datetime.datetime.today()

    active = 0

    totals = {}
    top_vcpu = []
    top_instances = []
    top_gigabytes = []
    top_quota_cores = []
    top_quota_instances = []
    top_quota_gigabytes = []

    for a in allocations_active:
        #        if a.allocation_home_display == site_name and a.status_display not in hide:
        if a.parent_request is None:
            if a.end_date is None:
                my_end = my_today
            else:
                my_end = datetime.datetime.strptime(a.end_date, '%Y-%m-%d')

            my_delta = my_today - my_end
            # Warning 4 week before expire
            # 1 month after warning quotas set to zero
            # 2 week after expire Vms stopped
            # 30 days after expire VMs deleted, to archive state (?)
            # 3 Months after all deleted , to deleted state

            # if my_delta.days < 30 and my_delta.days != 0:
            if my_delta.days < 30:
                print(
                    a.id, a.associated_site, a.national, a.project_name,
                    a.start_date, a.end_date, a.submit_date, a.status, a.status_display,
                    a.allocation_home_display, a.provisioned, my_delta.days,
                    a.parent_request, a.project_id
                )
                active += 1
                p_resources = project_resources(os_conn, a.project_id)

                print(a.national, type(a.national))

                # Counting totals
                for k in p_resources.keys():
                    if k in totals.keys():
                        totals[k] += p_resources[k]
                    else:
                        totals[k] = p_resources[k]

                # Keeping top ones
                top_vcpu = top_ones(10, p_resources, 'vcpus', a.project_id, a.project_name, top_vcpu)
                top_instances = top_ones(10, p_resources, 'instances', a.project_id, a.project_name, top_instances)
                top_gigabytes = top_ones(10, p_resources, 'gigabytes', a.project_id, a.project_name, top_gigabytes)
                top_quota_cores = top_ones(10, p_resources, 'quota_cores', a.project_id, a.project_name, top_quota_cores)
                top_quota_instances = top_ones(10, p_resources, 'quota_instances', a.project_id, a.project_name, top_quota_instances)
                top_quota_gigabytes = top_ones(10, p_resources, 'quota_gigabytes', a.project_id, a.project_name, top_quota_gigabytes)
                print()

        if active == 20:
            break
    print(totals)
    print("Top vcpus")
    for i in top_vcpu:
        print("    ", i)
    print("Top Instances")
    for i in top_instances:
        print("    ", i)
    print("Top Gigabytes")
    for i in top_gigabytes:
        print ("    ", i)
    print("Top quota vcpus")
    for i in top_quota_cores:
        print("    ", i)
    print("Top quota instances")
    for i in top_quota_instances:
        print("    ", i)
    print("Top quota Gigabyates")
    for i in top_quota_gigabytes:
        print("    ", i)

    print("Active allocations", active)


if __name__ == '__main__':
    sys.exit(main())
