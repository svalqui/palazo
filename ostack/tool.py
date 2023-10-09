# Copyright 2017 - 2023 by Sergio Valqui. All rights reserved.
#
# References
# https://docs.openstack.org/python-keystoneclient/latest/using-sessions.html
# https://docs.openstack.org/api-ref/identity/v3/#identity-api-operations
# https://docs.openstack.org/api-quick-start/
# https://docs.openstack.org/python-novaclient/stein/reference/api/novaclient.v2.servers.html
# https://docs.openstack.org/api-ref/compute/#list-servers
#
# https://github.com/NeCTAR-RC/python-nectarallocationclient
import datetime
import os
import sys

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as ks_client

import novaclient
from novaclient import client as nov_cli
from cinderclient import client as cin_cli
from nectarallocationclient import client as allo_client
from glanceclient import client as gla_cli

from os import path
import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )


from time import sleep

from tools.util_obj import print_structure
from tools.util_obj import print_structure_det
from tools.util_obj import look_for_obj_by_att_val

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


def prj_det(ks_client, p_name, my_session):
    """Print project details."""

    q_prjs = ks_client.projects.list(name=p_name)
    my_prj = q_prjs.data[0]
    # print_structure(my_prj.data[0])

    if hasattr(my_prj, 'allocation_id'):
        allo_brief(my_session, my_prj.allocation_id)
    nova_cli = nov_cli.Client(version=2, session=my_session)
    cinder_cli = cin_cli.Client(version=3, session=my_session)
    quota_brief(nova_cli, cinder_cli, my_prj.id)

    prj_vols = cinder_cli.volumes.list(search_opts={'project_id': my_prj.id, 'all_tenants': 1})
    print("prj vols ", len(prj_vols))
    # print_structure(prj_vols[0])

    print("VMs :")
    server_list_per_prjid(nova_cli, my_prj.id)
    print()

    return


def prj_list(ks_client):
    """Print a list of all projects, Requires ADMIN Credentials."""

    prjs = ks_client.projects.list()
    # print_structure(prjs.data[0])
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


def prj_list_by_az(ks_cli, az_name):  # todo: filter by availability zone no working
    """Print a list of all projects by availability zone, Requires ADMIN Credentials."""

    prjs = ks_cli.projects.list(compute_zones=az_name)

    # print_structure(prjs.data[0])
    for i in prjs.data:
        print(i.id, i.name, i.description)
        print_structure(i,True)
        break
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
    assigns = ks_cli.role_assignments.list(user=my_user.data[0].id)
    roles = ks_cli.roles.list()
    u_projects = ks_cli.projects.list(user=my_user.data[0].id)

    for assign in assigns.data:
        print(look_for_obj_by_att_val(roles.data, 'id', assign.role['id']).name,
              my_user.data[0].name,
              look_for_obj_by_att_val(u_projects.data, 'id', assign.scope['project']['id']).name
              )

    return ()


def assigned_usr_resources(my_session, os_user_name):
    """List projects for a user including Project brief, VMs."""

    ks_cli = ks_client.Client(session=my_session, include_metadata=True)
    my_user = ks_cli.users.list(name=os_user_name)
    assigns = ks_cli.role_assignments.list(user=my_user.data[0].id)
    roles = ks_cli.roles.list()
    u_projects = ks_cli.projects.list(user=my_user.data[0].id)
    usr_prj_ids = []

    # Projects and Roles
    print("User: ", os_user_name)
    print("Roles:")
    for assign in assigns.data:
        prj_name = look_for_obj_by_att_val(u_projects.data, 'id', assign.scope['project']['id']).name
        role_name = look_for_obj_by_att_val(roles.data, 'id', assign.role['id']).name

        print(prj_name,
              role_name,
              )
        if assign.scope['project']['id'] not in usr_prj_ids:
            usr_prj_ids.append(assign.scope['project']['id']),

    # Servers on a Project
    print()
    for prj_id in usr_prj_ids:
        prj = look_for_obj_by_att_val(u_projects.data, 'id', prj_id)
        print("Project: ", prj.name, prj.id)
        if hasattr(prj, 'allocation_id'):
            allo_brief(my_session, prj.allocation_id)
        nova_cli = nov_cli.Client(version=2, session=my_session)
        cinder_cli = cin_cli.Client(version=3, session=my_session)
        quota_brief(nova_cli, cinder_cli, prj_id)

        print("VMs :")
        server_list_per_prjid(nova_cli, prj_id)
        print()

    return ()


def user_list(ks_cli):
    """Print a list of all users, Requires ADMIN Credentials."""

    users = ks_cli.users.list()
    # print_structure(users.data[0],geta=False)
    for i in users.data:
        print(i.id, i.name, i.enabled)

    return


def get_ip_dns_name(svr_dns_name):
    """get the IP address given the DNS name"""
    import socket
    ip = ''
    ip_list = list({addr[-1][0] for addr in socket.getaddrinfo(svr_dns_name, 0, 0, 0, 0)})
    if len(ip_list) > 0:
        ip = ip_list[0]
    return ip


def server_prj_det_by_dnsname(svr_dns_names, my_session):
    print(my_session)
    nova = nov_cli.Client(version=2, session=my_session)
    print(
        "svr_ip, svr_id, svr_name, prj_id, prj_name, prj_des, usr_id, usr_name, usr_email, usr_full_name, user_enabled")
    for dns_name in svr_dns_names:
        svr_ip = get_ip_dns_name(dns_name)
        # print("svr_ip", svr_ip)
        svrs = nova.servers.list(search_opts={'access_ip_v4': svr_ip, 'all_tenants': 1})
        # print('no svrs :', len(svrs))
        my_server = svrs[0]
        # print(my_server.name, my_server.id, my_server.accessIPv4, my_server.tenant_id, my_server.user_id)

        ks_cli = ks_client.Client(session=my_session, include_metadata=True)

        prj = ks_cli.projects.get(my_server.tenant_id)
        # print(prj.data.id, prj.data.name, prj.data.description)

        user = ks_cli.users.get(my_server.user_id)
        # print(user.data.id, "Username:", user.data.name, "Email:",user.data.email, "FullName:",user.data.full_name, "Enabled:", user.data.enabled)

        # print_structure(user.data, True)

        line = svr_ip + ", " + my_server.id + ", " + my_server.name + ", " + prj.data.id + ", " + prj.data.name + \
               ", " + prj.data.description + ", " + user.data.id + ", " + user.data.name + ", " + user.data.email + \
               ", " + user.data.full_name + ", " + str(user.data.enabled)

        print(line)

    return ()


def server_prj_det_by_ip(svr_ip_adds, my_session):
    """Server and Project Details by IP addresses"""

    nova = nov_cli.Client(version=2, session=my_session)
    print(
        "svr_ip, svr_id, svr_name, svr_status, prj_id, prj_name, prj_des, prj_contact"
        ", usr_name, usr_email, usr_full_name, user_enabled")
    ks_cli = ks_client.Client(session=my_session, include_metadata=True)
    allo_cli = allo_client.Client(version=1, session=my_session)

    for my_ip in svr_ip_adds:
        # print(my_ip)
        svrs = nova.servers.list(search_opts={'access_ip_v4': my_ip, 'all_tenants': 1})
        # TODO for some reason returns a list of various VMs, some don't exist, others have similar regexp
        # print(len(svrs))
        # filtering exact match
        my_server = look_for_obj_by_att_val(svrs, 'accessIPv4', my_ip)
        # print(my_server.name, my_server.id, my_server.accessIPv4, my_server.tenant_id, my_server.user_id)

        prj = ks_cli.projects.get(my_server.tenant_id)
        # print(prj.data.id, prj.data.name, prj.data.description)
        # print(prj.data.allocation_id)

        if prj.data.name == 'trove':
            #print_structure(my_server)
            # if is trove reload project with user's project, not trove project details
            usr_prj = my_server.metadata['project_id']
            prj = ks_cli.projects.get(usr_prj)

            # reload allocation details
            if hasattr(prj.data, 'allocation_id'):
                my_allo = allo_cli.allocations.get(prj.data.allocation_id)
                prj_contact_email = my_allo.contact_email
            else:
                prj_contact_email = "None"
        else:

            if hasattr(prj, 'allocation_id'):
                my_allo = allo_cli.allocations.get(prj.data.allocation_id)
                prj_contact_email = my_allo.contact_email
            else:
                prj_contact_email = "None"

        user = ks_cli.users.get(my_server.user_id)
        # print(user.data.id, "Username:", user.data.name, "Email:",user.data.email, "FullName:",user.data.full_name, "Enabled:", user.data.enabled)

        # print_structure(user.data, True)

        if 'email' in dir(user.data):
            usr_email = user.data.email
        else:
            usr_email = "No-email"

        if 'full_name' in dir(user.data):
            usr_f_name = user.data.full_name
        else:
            usr_f_name = ""

        line = my_ip + ", " + my_server.id + ", " + my_server.name + ", " + my_server.status + ", " + \
               prj.data.id + ", " + prj.data.name + ", " + prj.data.description + ", " + prj_contact_email + ", " + \
               user.data.name + ", " + usr_email + ", " + usr_f_name + ", " + str(user.data.enabled)

        print(line)

    return ()

def server_list_per_az(av_zone, nv_client): # todo: filter by availability zone
    # This doesn't work availability zone doesn;t filter properly
    # svrs = nv_client.servers.list(search_opts={'availability_zone': av_zone, 'all_tenants': 1})
    svrs = nv_client.servers.list(search_opts={'all_tenants': 1})
    for count, svr in enumerate(svrs):
        print(count, svr.id, getattr(svr, "OS-EXT-AZ:availability_zone"), svr.addresses)

    return ()


def server_list_per_prjid(my_session, prj_id):
    """List servers on the given project-id."""
    nv_client = nov_cli.Client(version=2, session=my_session)
    svrs = nv_client.servers.list(search_opts={'project_id': prj_id, 'all_tenants': 1})
    gl_client = gla_cli.Client(version=2, session=my_session)
    ci_client = cin_cli.Client(version=3, session=my_session)

    for counter, svr in enumerate(svrs):
        av_zone = getattr(svr, "OS-EXT-AZ:availability_zone")
        # locked = getattr(svr, "locked") # it seems it can't be queried
        # print_structure(svr, True)
        # get the flavor obj to get the name, base only have id
        svr._info["flavor"] = nv_client.flavors.get(svr._info["flavor"]["id"])
        inst_vols = getattr(svr, "os-extended-volumes:volumes_attached")

        if svr.image:
            try:
                my_image = gl_client.images.get (svr.image["id"])
                display_image = my_image.name
            except Exception as e:
                # print(type(exception).__name__)
                display_image = "No_Image_ID_Found"
        else:
            display_image = "No_Image"
            if len(inst_vols) > 0:
                first_disk_id = inst_vols[0]['id']
                my_vol = ci_client.volumes.get(first_disk_id)
                if hasattr(my_vol, 'volume_image_metadata'):
                    if 'image_name' in my_vol.volume_image_metadata.keys():
                        display_image = my_vol.volume_image_metadata['image_name']
                    else:
                        display_image = "No image name for vol"
                else:
                    display_image = "No image on vol metadata"



        if svr.key_name:
            display_key = svr.key_name
        else:
            display_key = "No_ssh_key"
        print(
            #counter + 1,
            svr.id, svr.name,
            svr.status,
            av_zone,
            svr._info["flavor"].name,
            #svr.addresses,
            svr.accessIPv4,
            display_image,
            #svr.security_groups,
            #svr.metadata,
            len(inst_vols),
        )

        if len(inst_vols) > 0:
            for inst_vol in inst_vols:
                #print("    vol_att_id:", inst_vol['id'])
                break


    # print_structure(svrs[0])
    return ()


def server_status(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    # print_structure(my_svr)
    print(my_svr.id, my_svr.name, getattr(my_svr, "OS-EXT-STS:vm_state"), my_svr.status)

    return ()


def server_det_basic(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    # print_structure(my_svr)
    print(my_svr.id, my_svr.name, my_svr.status, my_svr.addresses)

    return ()


def server_det_obj(svr_id, nv_client):
    my_svr = nv_client.servers.get(svr_id)
    print_structure(my_svr)

    return ()


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

    return ()


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

    return ()


def flavor_det(nv_client):
    """Lists the flavors"""
    # (is_public=None) For Admin lists all flavors
    flavors = nv_client.flavors.list(is_public=None)

    for f in flavors:
        print(f.name, f.id, f.vcpus, f.ram)
    return ()


def flavor_prjs(my_session, prj_id):
    """Lists of active flavors for the given project."""
    #
    nov = nov_cli.Client(version=2, session=my_session)
    ks = ks_client.Client(session=my_session, include_metadata=True)
    all_fla = nov.flavors.list(is_public=None)  #todo where "is_public" comes from?
    #all_fla = nov.flavors.list()
    print("All flavors ", len(all_fla))
    print("Project :", prj_id, " has these flavors :")

    for f in all_fla:
        is_public = getattr(f, "os-flavor-access:is_public")
        # print(f.name, is_public)
        if not is_public:  # Not public, Access list not available for public flavors
            fla_acl = nov.flavor_access.list(flavor=f)
            # print(len(fla_acl))
            for acl in fla_acl:
                if acl.tenant_id == prj_id:
                    print(f.name, "Ram ", f.ram, "vcpu ", f.vcpus, )

    return ()

def allo_per_site(my_session, my_associated_site):
    """Allocation report per a given site"""
    allo_cli = allo_client.Client(version=1, session=my_session)

    print("Getting Allocations")
    allocations = allo_cli.allocations.list(associated_site=my_associated_site,
                                            provisioned=False,
                                            )

    # index allocations by allocation id
    allocations_dict = {}
    for allocation in allocations:
        allocations_dict[allocation.id] = allocation

    hide =["Deleted", "Approved" ]

    my_today = datetime.datetime.today()

    for a in allocations:
#        if a.allocation_home_display == site_name and a.status_display not in hide:
        if a.parent_request is None:

            if a.end_date is None:
                my_end = my_today
            else:
                my_end = datetime.datetime.strptime(a.end_date, '%Y-%m-%d')

            my_delta = my_today - my_end
            if my_delta.days < 60 and my_delta.days != 0:
                print(
                    a.id, a.associated_site, a.national, a.project_name,
                    a.start_date, a.end_date, a.submit_date, a.status, a.status_display,
                    a.allocation_home_display, a.provisioned, my_delta.days,
                    a.parent_request
                )
    return ()


def allo_per_approver(my_session, my_email):
    """Allocation report per a approver email"""
    allo_cli = allo_client.Client(version=1, session=my_session)

    print("Getting Allocations")
    allocations = allo_cli.allocations.list(associated_site='uom',
                                            status="A",
                                            approver_email=my_email
                                            )
    # allocations.filter(parent_request=None).filter(status__in=('A', 'X', 'J')).order_by('project_name')

    print("Length of allocations: ", len(allocations))

    hide = ["Deleted", "Approved"]

    my_today = datetime.datetime.today()

    print("Filtering allocations ...")
    for a in allocations:
        #        if a.allocation_home_display == site_name and a.status_display not in hide:
        if a.status == "A":
            print(a.id, a.associated_site, a.national, a.project_name,
                  a.start_date, a.end_date, a.submit_date, a.status,
                  a.status_display, a.allocation_home_display, a.provisioned,
                  a.approver_email
                  )
    return ()


def allo_per_prj_name(my_session, prj_name):
    """Allocation details for a given project name."""
    allo_cli = allo_client.Client(version=1, session=my_session)
    ks_cli = ks_client.Client(session=my_session, include_metadata=True)

    print("Getting the project...")
    my_prj = ks_cli.projects.list(name=prj_name)
    # print_structure(my_prj)

    print(" Project Name ", my_prj.data[0].name)
    print(" Project id ", my_prj.data[0].id)
    print(" Project allocation id ", my_prj.data[0].allocation_id)

    my_all_id = my_prj.data[0].allocation_id

    print("Getting the allocation...")
    my_allo = allo_cli.allocations.get(my_all_id)
    print("allocation_home ", my_allo.allocation_home)
    print("allocation_home_display ", my_allo.allocation_home_display)
    print("associated_site ", my_allo.associated_site)
    print("chief_investigator ", my_allo.chief_investigator)
    print("national ", my_allo.national)
    print("contact ", my_allo.contact_email)
    print("status ", my_allo.status)
    print("end date ", my_allo.end_date)
    print("status_display ", my_allo.status_display)
    print("provisioned ", my_allo.provisioned)
    print("duration ", my_allo.estimated_project_duration, " Months")
    print()

    # get works , need allocation id
    # allo_per_prj_name = allo.allocations.get('105619')
    # works but returns all, needs review
    # allo_per_prj_name = allo.allocations.list(search_opts={'project_id': prj_id, 'all_tenants': 1})

    return ()




def allo_brief(my_session, allo_id):
    """Allocation brief by allocation ID."""
    allo_cli = allo_client.Client(version=1, session=my_session)
    print("Getting allocation...")
    my_allo = allo_cli.allocations.get(allo_id)
    print("allocation_home ", my_allo.allocation_home)
    print("allocation_home_display ", my_allo.allocation_home_display)
    print("associated_site ", my_allo.associated_site)
    print("chief_investigator ", my_allo.chief_investigator)
    print("national ", my_allo.national)
    print("contact ", my_allo.contact_email)
    print("status ", my_allo.status)
    print("end date ", my_allo.end_date)
    print()

    return ()


def quota_brief(nv_client, cin_client, prj_id):
    """Quota brief by Project ID."""

    my_nv_quota = nv_client.quotas.get(prj_id)
    my_ci_quota = cin_client.quotas.get(prj_id)

    my_vols = cin_client.volumes.list()
    print("vols len ", len(my_vols))

    # print_structure(my_ci_quota)
    print("cores", my_nv_quota.cores)
    print("gigabytes", my_ci_quota.gigabytes)
    print("instances", my_nv_quota.instances)
    print("ram", my_nv_quota.ram)
    print()

def sec_per_svrid(my_session, svr_id):
    """Security groups per project id"""
    nov = nov_cli.Client(version=2, session=my_session)
    svr = nov.servers.get(svr_id)
    sec_grps = svr.list_security_group()
    for i in sec_grps:
        print(i)
        print(i.name)
        print(i.description)
        for r in i.rules:
            #print(r)
            print(r['ip_protocol'], r['from_port'], r['to_port'], r['ip_range'])
            # print_structure_det(r)
        print()


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
    # assign_list(ks_cli) # Needs link to role.id, project.id, user.id

    # nova = nov_cli.Client(version=2, session=my_session)

    # svrs = nova.servers.list(search_opts={'all_tenants': 'yes'})
    # len(svrs)

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

    # ci_client = cin_cli.Client(version=3, session=my_session)

    ## works
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_det_basic('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_stop('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # av_zone = input("av zone :")
    # server_list_per_az(av_zone, nv_client)

    print("(s) Servers, look for server names matching \n"
          "(sd) Server details by server id, all obj att \n"
          "(p) Projects, look for project names matching \n"
          "(pd) prj det, show project details for the given project name \n"
          "(pbip) Project and Server Details by list of VM IPs ([ip1,ip2....]) \n"
          "(sp) Servers in Prj, for a given Prj-id\n"
          "(r) user role assignment, \n"
          "(ur) User resources, \n"
          "(f) Flavors, \n"
          "(fa) Flavor accessed by a Project-id, \n"
          "(ai) allocation brief by allocation id\n"
          "(an) allocation brief by project name\n"
          "(ar) allocation report per site name\n"
          "(aa) allocation report per approver email\n"
          "(paz) projects per availability zone\n"
          "(sec) security groups per srv_id\n")

    look_in = input(" your choice: ")
    look_for = input("Search for :")

    ips = [

    ]

    if look_in == "s":
        sleep(1)
    elif look_in == "sd":
        server_det_obj(look_for, nv_client)
    elif look_in == "p":
        sleep(1)
    elif look_in == "pd":
        prj_det(ks_cli, look_for, my_session)
    elif look_in == "pbip":
        server_prj_det_by_ip(ips, my_session)
    elif look_in == "sp":
        server_list_per_prjid(my_session, look_for)
    elif look_in == "r":
        assigns_search(ks_cli, look_for)
    elif look_in == "f": # flavor details
        flavor_det(nv_client)
    elif look_in == "fa":  # Flavor Accessed by Project-id
        flavor_prjs(my_session, look_for)
    elif look_in == "ur": # User resources, role, projects, allocations, servers
        assigned_usr_resources(my_session, look_for)
    elif look_in == "ai": # allocation brief by allocation id
        allo_brief(my_session, look_for)
    elif look_in == "an":  # allocation brief by project name
        allo_per_prj_name(my_session, look_for)
    elif look_in == "ar": # allocation report per site name
        allo_per_site(my_session, look_for)
    elif look_in == "aa":  # allocation report per approver email
        allo_per_approver(my_session, look_for)
    elif look_in == "paz": # Projects per availability zone
        prj_list_by_az(ks_cli, look_for)
    elif look_in == "sec": # security groups per svr_id
        sec_per_svrid(my_session, look_for)

    else:
        print("No option available")


if __name__ == '__main__':
    sys.exit(main())
