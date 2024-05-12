import openstack
import sys
import time
import datetime

def main():
    os_conn = openstack.connect(cloud='envvars')

    source_host = input('which host to evacuate: ')

    servers_host = os_conn.list_servers(
        all_projects=True,
        filters={'host': source_host}
    )

    n_servers = len(servers_host)
    print(n_servers)
    for idx, server in enumerate(servers_host):
        print ("---v ", idx+1 ," of ", n_servers)
        if server.status == "ACTIVE": # If active migrate
            print(datetime.datetime.time.now(), "Migrating ", server.id, server.name, " from: ", source_host, )

            server.live_migrate(session=os_conn.session, host=None, force=None, block_migration='auto')

            my_svr_state = getattr(server, "OS-EXT-STS:vm_state")
            my_svr_host = getattr(server, "OS-EXT-SRV-ATTR:host")
            my_server = os_conn.get_server(server.id)

            while my_server.status == "MIGRATING":
                time.sleep(5)
                # refresh values
                my_server = os_conn.get_server(server.id)
                print(
                    "  Still migrating ",
                    server.id,
                    " state ",
                    my_svr_state,
                    " host: ",
                    my_svr_host
                )

        my_server = os_conn.get_server(server.id)
        print(
            "Migrated ",
            my_server.id,
            my_server.name,
            my_server.status,
            getattr(my_server, "OS-EXT-SRV-ATTR:host"),
        )


if __name__ == '__main__':
    sys.exit(main())



