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


def print_structure(my_obj, geta=True):
    """Prints attributes of an Obj."""
    for att in dir(my_obj):
        if geta:
            print(att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)
        else:
            print(att, type(getattr(my_obj, att)).__name__)


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


def prj_list(ks_client):
    """Print a list of all projects"""

    prjs = ks_client.projects.list()
    #print_structure(prjs.data[0])
    print_structure(ks_client.projects)
    for i in prjs.data:
        print(i.id, i.name, i.description)
    ## Projects
    #    Attributes:
    #        * id: a uuid that identifies the project
    #        * name: project name
    #        * description: project description
    #        * enabled: boolean to indicate if project is enabled
    #        * parent_id: a uuid representing this project's parent in hierarchy
    #        * parents: a list or a structured dict containing the parents of this
    #                   project in the hierarchy
    #        * subtree: a list or a structured dict containing the subtree of this
    #                   project in the hierarchy
    # COntain other attributes from parent such:
    return


def user_list(ks_cli):
    """Print a list of all users"""

    users = ks_client.users.list()
    # print_structure(users.data[0],geta=False)
    for i in users.data:
        print(i.id, i.name, i.enabled)

    return


def assig_list(ks_cli):
    """Print role assignments per user"""
#    role_assigns = ks_client.role_assignments.list(include_names=True) # Doesn't work
#    role_assigns = ks_client.role_assignments.list()  # Works
#    role_assigns = ks_client.role_assignments.RoleAssignmentManager.list(include_names=True) # Doesn't work
    role_assigns = ks_client.role_assignments.list()
    print_structure(role_assigns, geta=False)
    print(len(role_assigns.data))
    print("***")
    print_structure(role_assigns.data[0])
    print("++++")
    print(role_assigns.data[0])
    return


def main():
    """ CLI implementation temporal for fast trial while developing
    """
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])

    # Authenticate using environmental variables
    my_session = os_auth_env()

    # Create a keystone client interface
    # https://docs.openstack.org/python-keystoneclient/latest/api/keystoneclient.v3.html#module-keystoneclient.v3.client
    ks_cli = ks_client.Client(session=my_session, include_metadata=True)

    prj_list(ks_cli)

    #user_list(ks_cli)
    # assig_list(ks_cli)


if __name__ == '__main__':
    sys.exit(main())
