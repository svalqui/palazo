# Copyright 2017 - 2021 by Sergio Valqui. All rights reserved.
#
# References
# https://docs.openstack.org/python-keystoneclient/latest/using-sessions.html
# https://docs.openstack.org/api-ref/identity/v3/#identity-api-operations
# https://docs.openstack.org/api-quick-start/

import os
import sys

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as ks_client


def look_for_obj_by_att_val(my_obj_list, my_att, my_value):
    """Search for an Obj with an attribute of a given value, for methods that return list of Obj."""

    ret_obj = None
    for my_obj in my_obj_list:
        if my_att in dir(my_obj):
            # print(getattr(my_obj, my_att), my_value)
            if getattr(my_obj, my_att) == my_value:
                ret_obj = my_obj
                break
    return ret_obj


def print_structure(my_obj):
    """Prints attributes of an Obj."""
    for att in dir(my_obj):
        print(att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)


def os_auth_env():
    """Authenticates using keystone, using environmental variables. returns a session"""
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       username=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'],
                       user_domain_id='default')
    #                   project_domain_id='default')
    #                   user_domain_id=os.environ['OS_USER_DOMAIN_NAME'])
    os_session = session.Session(auth=auth)
    print(os_session)

    return os_session


def main():
    """ CLI implementation temporal for fast trial while developing
    """
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])

    ks = ks_client.Client(session=os_auth_env(), include_metadata=True)
    print_structure(ks)

#    prjs = ks.projects.list()
#    print(prjs.data)
    # users = ks.users.list()


if __name__ == '__main__':
    sys.exit(main())
