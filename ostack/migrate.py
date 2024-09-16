# Only for migrating Vms out from hosts
# nova.aggregates.list() , list of aggregate objects, aggregate object have a list of host aggregate.hosts()
#
# https://docs.openstack.org/api-ref/compute/#list-servers
# https://docs.openstack.org/api-ref/compute/?expanded=list-servers-detail#list-server-request
#
#
# nv_client.servers.list(search_opts={'host': host_name, 'all_tenants': 1})
#
# class novaclient.v2.servers.Server(manager, info, loaded=False, resp=None)
# live_migrate(host=None, block_migration=None)

import os
import random
import sys
import time
import datetime

from keystoneauth1.identity import v3
from keystoneauth1 import session

from novaclient import client as nov_cli


def print_structure(my_obj, geta=True):
    """Prints attributes of an Obj."""
    for att in dir(my_obj):
        if geta:
            print(att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)
        else:
            print(att, type(getattr(my_obj, att)).__name__)

def os_auth_env_sess():
    """Authenticates using keystone, using environmental variables. returns a session"""
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       username=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'],
                       user_domain_id='default')
    os_session = session.Session(auth=auth)

    return os_session

def server_list_per_host(nv_client, my_host):
    """List servers on the given host."""
    svrs = nv_client.servers.list(search_opts={'host': my_host, 'all_tenants': 1})

    for counter, svr in enumerate(svrs):
        av_zone = getattr(svr, "OS-EXT-AZ:availability_zone")
        # locked = getattr(svr, "locked") # it seems it can't be queried
        # print_structure(svr)
        print(counter + 1, svr.id, svr.name, svr.status, av_zone,
              svr.addresses)
              # svr.addresses, svr.security_groups, svr.metadata)
        #inst_vols = getattr(svr, "os-extended-volumes:volumes_attached")
        #if len(inst_vols) > 0:
        #    for inst_vol in inst_vols:
        #        print("    vol_att_id:", inst_vol['id'])
    # print_structure(svrs[0])
    return svrs

def put_in_main_agg(nv_client, my_host):
    """Put the host in maintenance."""
    all_aggre = nv_client.aggregates.list()
    current_aggre= []
    current_aggre_names = []
    for agg in all_aggre:
        print("Checking Agg ", agg.name, agg)
        if "uom" in agg.name:
            print("    in uom agg")
            # aggre = nv_client.aggregates.get(agg_name)
            if my_host in agg.hosts:
                print("    Host", my_host, "is in agg")
                current_aggre.append(agg)
                current_aggre_names.append(agg.name)
    # put in main
    for a in current_aggre:
        print('Current Aggregates :', a.id, a.name)
        if 'maintenance' not in a.name:

            print('adding :', my_host, ' to: maintenance')
            nv_client.aggregates.add_host('aggregte-maint-id', my_host)

        # remove of all others
            for current_a in current_aggre:
                print('removing :', my_host, ' from: ', current_a.id, current_a.name )
                nv_client.aggregates.remove_host(current_a.id, my_host)
    return

def main():
    """ CLI implementation temporal for fast trial while developing
    """
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])
    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    nv_client = nov_cli.Client(version=2, session=my_session)

    # input source host here
    source_host = input('which host to evacuate: ')
    # input target host here
    #target_hosts = input('into which hosts(,): ')
    #target_hosts = [ 'qh2-rcc03', 'qh2-rcc04', 'qh2-rcc05' ]
    target_host = ''

    # List servers on host
    servers = server_list_per_host(nv_client, source_host)


    # check source host is on maintenance aggregate, if not
    # move the source host to the maintenance aggregate, add to maintenance remove from current

    # put_in_main_agg(nv_client, source_host)

    n_servers = len(servers)
    for idx, server in enumerate(servers):
        # line = " " + server.id + ", " + server.name + ", " + server.status + ", "
        # print(line)

#        if target_host != '':
#            target_host = random.choice(target_host)
        print ("---v ", idx+1 ," of ", n_servers)
        if server.status == "ACTIVE": # If active migrate
            print ("Migrating ", server.id, server.name, " from: ", source_host, " to ", target_host)
            if target_host != '':
                server.live_migrate(host=target_host)
            else:
                server.live_migrate()
            my_svr_state = getattr(server, "OS-EXT-STS:vm_state")
            my_svr_host = getattr(server, "OS-EXT-SRV-ATTR:host")
            # print(server.id, " state ", my_svr_state, " host: ", my_svr_host)
            time.sleep(10)
            my_server = nv_client.servers.get(server.id)
            # print(my_server.status)
            while my_server.status == "MIGRATING":
                time.sleep(10)
                # refresh values
                my_server = nv_client.servers.get(server.id)
                print("  ", datetime.datetime.now(), " Still migrating ", server.id, " state ", my_svr_state, " host: ", my_svr_host)
        elif server.status == "SHUTOFF" and server.id != '78fbd971-bfac-471b-a142-43cc825008f2':
            print(server.id, " SHUTOFF , switching on")
            server.start()
            time.sleep(20)
            my_server = nv_client.servers.get(server.id)
            print(my_server.status)
            if my_server.status == "ACTIVE":
                print(datetime.datetime.now(), "Migrating ", my_server.id, my_server.name, " from: ", source_host, " to ", target_host)
                if target_host != '':
                    server.live_migrate(host=target_host)
                else:
                    server.live_migrate()
                my_svr_state = getattr(my_server, "OS-EXT-STS:vm_state")
                my_svr_host = getattr(my_server, "OS-EXT-SRV-ATTR:host")
                # print(my_server.id, " state ", my_svr_state, " host: ", my_svr_host)
                time.sleep(10)
                my_server = nv_client.servers.get(server.id) # refresh values
                print(my_server.status)
                while my_server.status == "MIGRATING":
                    time.sleep(5)
                    # refresh values
                    my_server = nv_client.servers.get(server.id)
                    print("  Still migrating ", server.id, " state ", my_svr_state, " host: ", my_svr_host)
            print(server.id, " , switching OFF")
            server.stop()
            time.sleep(10)
            # todo : wait till stop before continue or time it out.
            for i in range (2):
                my_server = nv_client.servers.get(server.id)
                print("Still switching off ", my_server.id, " is ", my_server.status)
                time.sleep(10)

        # todo : include paused
        # todo : what to do with ERROR hosts? need re-set state, but maybe underlying issue.

        my_server = nv_client.servers.get(server.id)
        print("Migrated ", my_server.id, my_server.name, my_server.status, getattr(my_server, "OS-EXT-SRV-ATTR:host") )

        print('Stopping 2 Secs')
        time.sleep(2)

if __name__ == '__main__':
    sys.exit(main())
