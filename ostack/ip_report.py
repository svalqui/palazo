import os
import sys
import time

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

def main():
    """ CLI implementation temporal for fast trial while developing
    """
    av_zone = input("Availability_zone :")

    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    nv_client = nov_cli.Client(version=2, session=my_session)


    servers = nv_client.servers.list(search_opts={'availability_zone': av_zone, 'all_tenants': 1})
    for server in servers:
        print(server.id)
        print_structure(server)
        break


if __name__ == '__main__':
    sys.exit(main())
