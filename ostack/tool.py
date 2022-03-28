# Copyright 2017 - 2022 by Sergio Valqui. All rights reserved.
#
# References
# https://docs.openstack.org/python-keystoneclient/latest/using-sessions.html
# https://docs.openstack.org/api-ref/identity/v3/#identity-api-operations
# https://docs.openstack.org/api-quick-start/
# https://docs.openstack.org/python-novaclient/stein/reference/api/novaclient.v2.servers.html

import os
import sys

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as ks_client

import novaclient
from novaclient import client as nov_cli
from cinderclient import client as cin_cli
from nectarallocationclient import client as allo_cli

from time import sleep


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


def os_auth_env_sess():
    """Authenticates using keystone, using environmental variables. returns a session"""
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       username=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'],
                       user_domain_id='default')
    #                   project_domain_id='default')
    #                   user_domain_id=os.environ['OS_USER_DOMAIN_NAME'])
    os_session = session.Session(auth=auth)

    return os_session


def prj_list(ks_client):
    """Print a list of all projects, Requires ADMIN Credentials."""

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
    # Contains other attributes from parent such:
    return


def assign_list(ks_cli):
    """Print role assignments per user, Requires ADMIN Credentials."""
#    role_assigns = ks_client.role_assignments.list(include_names=True) # Doesn't work
#    role_assigns = ks_client.role_assignments.list()  # Works
#    role_assigns = ks_client.role_assignments.RoleAssignmentManager.list(include_names=True) # Doesn't work
    role_assigns = ks_cli.role_assignments.list()
    print_structure(role_assigns, geta=False)
    print(len(role_assigns.data))
    print("***")
    print_structure(role_assigns.data[0])
    print("++++")
    print(role_assigns.data[0])
    ## Assignments
    # Attributes:
    #     * role: an object which contains a role uuid
    #     * user or group: an object which contains either a user or
    #                      group uuid
    #     * scope: an object which has either a project or domain object
    #              containing an uuid

    return


def assigns_search(ks_cli, os_user_name):
    """Print a list role assignments for a user."""

    my_user = ks_cli.users.list(name=os_user_name)
    print_structure(my_user.data[0])
    assigns = ks_cli.role_assignments.list(user=my_user.data[0].id)
    roles = ks_cli.roles.list()
    u_projects = ks_cli.projects.list(user=my_user.data[0].id)

    for assign in assigns.data:

        print(look_for_obj_by_att_val(roles.data, 'id', assign.role['id']).name, my_user.data[0].name,
              look_for_obj_by_att_val(u_projects.data, 'id', assign.scope['project']['id']).name)

    return()


def user_list(ks_cli):
    """Print a list of all users, Requires ADMIN Credentials."""

    users = ks_cli.users.list()
    # print_structure(users.data[0],geta=False)
    for i in users.data:
        print(i.id, i.name, i.enabled)

    return


def get_ip_dns_name(svr_dns_name):
    import socket
    ip = ''
    ip_list = list({addr[-1][0] for addr in socket.getaddrinfo(svr_dns_name, 0, 0, 0, 0)})
    if len(ip_list) > 0:
        ip = ip_list[0]
    return ip


def server_prj_det_by_dnsname(svr_dns_names, my_session):

    print(my_session)
    nova = nov_cli.Client(version=2, session=my_session)
    print("svr_ip, svr_id, svr_name, prj_id, prj_name, prj_des, usr_id, usr_name, usr_email, usr_full_name, user_enabled")
    for dns_name in svr_dns_names:

        svr_ip = get_ip_dns_name(dns_name)
        #print("svr_ip", svr_ip)
        svrs = nova.servers.list(search_opts={'access_ip_v4': svr_ip, 'all_tenants': 1})
        # print('no svrs :', len(svrs))
        my_server = svrs[0]
        #print(my_server.name, my_server.id, my_server.accessIPv4, my_server.tenant_id, my_server.user_id)

        ks_cli = ks_client.Client(session=my_session, include_metadata=True)

        prj = ks_cli.projects.get(my_server.tenant_id)
        #print(prj.data.id, prj.data.name, prj.data.description)

        user = ks_cli.users.get(my_server.user_id)
        #print(user.data.id, "Username:", user.data.name, "Email:",user.data.email, "FullName:",user.data.full_name, "Enabled:", user.data.enabled)

        #print_structure(user.data, True)

        line = svr_ip + ", " + my_server.id + ", " + my_server.name + ", " + prj.data.id + ", " + prj.data.name + \
               ", " + prj.data.description + ", " + user.data.id + ", " + user.data.name + ", " + user.data.email + \
               ", " + user.data.full_name + ", " + str(user.data.enabled)

        print(line)

    return ()


def server_list_per_az(av_zone, nv_client):

    # This doesn't work availability zone doesn;t filter properly
    # svrs = nv_client.servers.list(search_opts={'availability_zone': av_zone, 'all_tenants': 1})
    svrs = nv_client.servers.list(search_opts={'all_tenants': 1})
    for count, svr in enumerate(svrs):
        print(count, svr.id, getattr(svr, "OS-EXT-AZ:availability_zone"),svr.addresses)

    return()


def server_status(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    # print_structure(my_svr)
    print(my_svr.id, my_svr.name, getattr(my_svr, "OS-EXT-STS:vm_state"), my_svr.status)

    return()


def server_det_basic(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    # print_structure(my_svr)
    print(my_svr.id, my_svr.name, my_svr.status, my_svr.addresses)

    return()


def server_stop(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    att_sts = getattr(my_svr, "OS-EXT-STS:vm_state")
    if att_sts == 'stopped':
        print(svr_id, " Already stopped")
    elif att_sts == 'active':
        my_svr.stop()
        sleep(2)
        my_svr = nv_client.servers.get(svr_id)
        print(svr_id, getattr(my_svr, "OS-EXT-STS:vm_state"))
    else:
        print(svr_id, att_sts, " Not active nor stopped passing it")

    return()


def server_start(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    att_sts = getattr(my_svr, "OS-EXT-STS:vm_state")
    if att_sts == 'stopped':
        my_svr.start()
        sleep(2)
        my_svr = nv_client.servers.get(svr_id)
        print(svr_id, getattr(my_svr, "OS-EXT-STS:vm_state"))
    elif att_sts == 'active':
        print(svr_id, " Already active")
    else:
        print(svr_id, att_sts, " Not active nor stopped passing it")

    return()


def main():
    """ CLI implementation temporal for fast trial while developing
    """
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])

    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    # Create a keystone client interface
    # https://docs.openstack.org/python-keystoneclient/latest/api/keystoneclient.v3.html#module-keystoneclient.v3.client
    # ks_cli = ks_client.Client(session=my_session, include_metadata=True)

    # prj_list(ks_cli) # this works
    # user_list(ks_cli) # this works
    #assign_list(ks_cli) # Needs link to role.id, project.id, user.id

    # nova = nov_cli.Client(version=2, session=my_session)
    #print(len(nova.hypervisors.list()))

    #svrs = nova.servers.list(search_opts={'all_tenants': 'yes'})
    #len(svrs)

    # print_structure(nova.servers.list(search_opts={'access_ip_v4': '<ip>', 'all_tenants': 1}))
    # print()
    # svr = nova.servers.get('e4dd3cf4-4b44-417b-a989-abc5772372a1') # This works
    # svr = nova.servers.list(search_opts={'access_ip_v4': '10.10.10.10', 'all_tenants': 1})) # This works

    # This works
    # server_prj_det_by_dnsname(my_list, my_session)

    # Allocation works,
    ks_cli = ks_client.Client(session=my_session, include_metadata=True)
    # prj = ks_cli.projects.get(project='<prj_id>')
    #
    # my_alloc = allo_cli.Client(version=1, session=my_session)
    # print_structure(my_alloc.quotas.get('736470'), True)
    # print_structure(my_alloc.quotas.list(search_opts={'project_name':'<prj-name>>'}))

    nv_client = nov_cli.Client(version=2, session=my_session)

    ## works
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_det_basic('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_stop('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # av_zone = input("av zone :")
    # server_list_per_az(av_zone, nv_client)

    look_in = input("Servers (s), Projects(p), Servers in Prj (sp), user role assignment(r): ")
    look_for = input("Search for :")

    if look_in == "s":
        sleep(1)
    elif look_in == "p":
        sleep(1)
    elif look_in == "sp":
        sleep(1)
    elif look_in == "r":
        assigns_search(ks_cli, look_for)
    else:
        print("No option available")



if __name__ == '__main__':
    sys.exit(main())
