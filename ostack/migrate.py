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
import sys
import time

from keystoneauth1.identity import v3
from keystoneauth1 import session

from novaclient import client as nov_cli

def os_auth_env_sess():
    """Authenticates using keystone, using environmental variables. returns a session"""
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       username=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'],
                       user_domain_id='default')
    os_session = session.Session(auth=auth)

    return os_session

def main():
    """ CLI implementation temporal for fast trial while developing
    """
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])
    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    nv_client = nov_cli.Client(version=2, session=my_session)

    # List servers on host

    # input source host here
    source_host = ''
    # input target host here
    target_host = ''

    # check source host is on maintenance aggregate, if not
    # move the source host to the maintenance aggregate, add to maintenance remove from current

    #
    #
    servers = nv_client.servers.list(search_opts={'host': source_host, 'all_tenants': 1})
    for server in servers:
        # line = " " + server.id + ", " + server.name + ", " + server.status + ", "
        # print(line)
        print ("---")
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
                time.sleep(12)
                # refresh values
                my_server = nv_client.servers.get(server.id)
                print("  Still migrating ", server.id, " state ", my_svr_state, " host: ", my_svr_host)
        elif server.status == "SHUTOFF" and server.id != '78fbd971-bfac-471b-a142-43cc825008f2':
            print(server.id, " SHUTOFF , switching on")
            server.start()
            time.sleep(20)
            my_server = nv_client.servers.get(server.id)
            print(my_server.status)
            if my_server.status == "ACTIVE":
                print("Migrating ", my_server.id, my_server.name, " from: ", source_host, " to ", target_host)
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
                    time.sleep(10)
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




if __name__ == '__main__':
    sys.exit(main())
