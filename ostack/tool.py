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

import openstack

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
    """Print project details by project name."""

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

def is_mido(os_conn, prj_id):
    net = os_conn.network.get_network(prj_id)
    if net.provider_network_type == 'midonet':
        return True
    else:
        return False


def prj_net_det(os_conn, my_prj):
    project = os_conn.get_project(my_prj)
    net_leg_names = []
    if 'tags' in (dir(project)):
        if project.tags:
            if 'legacy-networking' in project.tags:
                print("Project:", project.name, "is legacy")
    nets = os_conn.network.networks(is_router_external=False, project_id=project.id)
    for n in nets:
        if n.provider_network_type == 'midonet':
            if n.name not in net_leg_names:
                net_leg_names.append(n.name)
            print("Legacy", n.resource_key, n.id, n.name, getattr(n, 'provider_network_type'),)
        else:
            print(n.resource_key, n.id, n.name,
                  getattr(n, 'provider_network_type'), )
        for s in n.subnet_ids:
            sub = os_conn.get_subnet(s)
            print("   ", sub.resource_key, sub.id, sub.name, sub.cidr)

    # nets_mido = os_conn.network.networks(provider_network_type='midonet')
    # for n in nets_mido:
    #    print(n.name,)

    rtrs = os_conn.network.routers(tenant_id=project.id)
    for r in rtrs:

        my_info = ''
        for i in r.external_gateway_info.keys():
            if i == 'network_id':
                if is_mido(os_conn,r.external_gateway_info[i]):
                    print("Legacy", r.resource_key, r.id, r.name, r.status, )
                else:
                    print(r.resource_key, r.id, r.name, r.status, )
                print('    network_id', r.external_gateway_info[i])

            elif i == 'external_fixed_ips':
                for ip in r.external_gateway_info[i]:
                    # print(ip)
                    print("        external_fixed_ips", ip['ip_address'])

    lbs = os_conn.load_balancer.load_balancers(project_id=project.id)
    for l in lbs:
        if is_mido(os_conn, l.vip_network_id):
            print("Legacy", l.resource_key, l.name, l.vip_address, l.vip_network_id)
        else:
            print(l.resource_key, l.name, l.vip_address, l.vip_network_id)

    ips = os_conn.network.ips(project_id=project.id)
    for i in ips:
        if is_mido(os_conn, i.floating_network_id):
            print("Legacy",
                  i.resource_key,
                  i.floating_ip_address,
                  i.status,
                  "Router",
                  i.router_id,
                  "Port",
                  i.port_id,
            )
        else:
            print(i.resource_key,
                  i.floating_ip_address,
                  i.status,
                  "Router",
                  i.router_id,
                  "Port",
                  i.port_id,
                  )

    print("List of VMs on Legacy Network")
    svrs = os_conn.list_servers(all_projects=True, filters={'project_id':project.id})
    print("servers", len(svrs))
    print()
    # print(dir(svrs[0]))
    print()
    print(svrs[0])
    print("servers in legacy Network: ")
    for s in svrs:
        svr_adds = ""
        is_leg = True
        for net in s.addresses.keys():
            svr_adds += net + " "
            if net in net_leg_names:
                is_leg = True
            for ips in s.addresses[net]:
                svr_adds += ips['addr'] + " "
        if is_leg:
            print(s.id, s.name, s.image, s.image_id, svr_adds)
            if s.image.id:
                print("    ", s.image.id)
                my_img = os_conn.get_image_by_id(s.image.id)
                print()
                print(my_img.name)

                print("$$$$")
                print ("    ",)

    return


def net_all(os_conn):
    """List all network resources."""
    nets = os_conn.network.networks(is_router_external=False, project_id=project.id)
    rtrs = os_conn.network.routers(tenant_id=project.id)
    lbs = os_conn.load_balancer.load_balancers(project_id=project.id)
    ips = os_conn.network.ips(project_id=project.id)


def ip_to_lb(os_conn, my_ip):
    """show lb and project details from IP"""
    
    # there are 2 types of lb
    # lbs = os_conn.load_balancer.load_balancers()
    # lbs = os_conn.load_balancer.amphorae()

    lbs = os_conn.load_balancer.amphorae()
    print(dir(lbs))




    for l in lbs:
        print(l)
#        print(l.resource_key, l.name, l.vip_network_id, l.vip_address,)



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

        if svr.accessIPv4:
            display_ip = svr.accessIPv4
        else:
            display_ip = svr.addresses[next(iter(svr.addresses))][0]['addr']

        print(
            #counter + 1,
            svr.id, svr.name,
            svr.status,
            av_zone,
            svr._info["flavor"].name,
            #svr.addresses,
            display_ip,
            display_image,
            display_key,
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


def server_by_ip(svr_ip, os_conn):
    my_filter = {'ip': svr_ip}
    p = os_conn.list_ports(filters={'fixed_ips': ['ip_address='+svr_ip]})
#    print(len(p))
#    print(p)
    print("port device_id: ", p[0].device_id)
    print("port project_id: ", p[0].project_id)
    print("port security_groups_ids: ", p[0].security_group_ids)
#    svr = os_conn.get_server(name_or_id=p[0].device_id, all_projects=True) #  needs filtering by project id

    for sec_group_id in p[0].security_group_ids:
        print("    ", sec_group_id)

        sg = os_conn.get_security_group(name_or_id=sec_group_id, filters={'project_id': p[0].project_id })

        for i in sg['security_group_rules']:
     #       print("   ", i)
#            if i['direction'] == 'ingress' and  i['remote_ip_prefix'] == '0.0.0.0/0':
            if i['direction'] == 'ingress':
                print("       ", i['remote_ip_prefix'], i['direction'],i['port_range_min'], i['port_range_max'])


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


def server_in_aggregate(os_conn, look_for, my_site=''):
    """list vms in aggregate"""
    my_aggres = os_conn.list_aggregates()
    total = 0
    my_flavors = {}
    include_contact = True
    if include_contact:
        # Get allocations
        print(datetime.datetime.now(), "Getting Allocations")
        allo_cli = allo_client.Client(version=1, session=os_conn.session)
        allocations = allo_cli.allocations.list(associated_site=my_site,)
        print(datetime.datetime.now(), "allocations", len(allocations))
        # index allocations by allocation id
        allocations_dict = {}
        for allocation in allocations:
            allocations_dict[allocation.id] = allocation

        # Getting Projects
        print(datetime.datetime.now(), "Getting Projects")
        projects = os_conn.list_prqqojects()
        print(datetime.datetime.now(), "projects", len(projects))

        # index projects by project.id
        projects_dict = {}
        for project in projects:
            projects_dict[project.id] = project

    for a in my_aggres:
        if look_for == a.name:
            for h in a.hosts:
                servers_host = os_conn.list_servers(
                    all_projects=True,
                    filters={'host': h}
                )
                for s in servers_host:
                    net = ''
                    allo_contact = ''
                    allo_end_date = ''
                    # one ip for now
                    net_keys = s.addresses.keys()
                    #print(net_keys, list(net_keys)[0])
                    if len(s.addresses) > 0:
                        net = s.addresses[list(net_keys)[0]][0]['addr']
                    else:
                        net = ''
                    if hasattr(projects_dict[s.project_id], 'allocation_id'):
                        if projects_dict[s.project_id].allocation_id in allocations_dict.keys():
                            if hasattr(allocations_dict[projects_dict[s.project_id].allocation_id], 'contact_email'):
                                allo_contact = allocations_dict[projects_dict[s.project_id].allocation_id].contact_email
                            else:
                                allo_contact = "No_contact_email_on_allocation_" + projects_dict[s.project_id].allocation_id
                            allo_end_date = allocations_dict[projects_dict[s.project_id].allocation_id].end_date
                        else:
                            allo_contact = "Allocation " + projects_dict[s.project_id].allocation_id + " Not in aggregate " + my_site

                    print(
                        h,
                        s.project_id,
                        s.id,
                        s.name,
                        s.status,
                        s.flavor.name,
                        net,
                        allo_contact,
                        allo_end_date,
                    )
                    if s.flavor.name in my_flavors.keys():
                        my_flavors[s.flavor.name] += 1
                    else:
                        my_flavors[s.flavor.name] = 1
                    total += 1
    print("Total:", total)
    for i in my_flavors.keys():
        print(i, my_flavors[i])

def flavor_det(nv_client):
    """Lists the flavors."""
    # (is_public=None) For Admin lists all flavors
    flavors = nv_client.flavors.list(is_public=None)

    for f in flavors:
        print(f.name, f.id, f.vcpus, f.ram)
    return ()

def flavor_aggregate(os_conn, look_for):
    """List flavors on aggregates"""
    my_flavs = os_conn.list_flavors()
    my_aggres = os_conn.list_aggregates()
    aggregate_classname = {}
    for a in my_aggres:
        if a.availability_zone:
            # print(a.name, a.availability_zone)
            if look_for in a.availability_zone:
                if a.metadata:
                    if 'flavor' in a.metadata.keys():
                        if a.metadata['flavor'] in aggregate_classname.keys():
                            aggregate_classname[a.metadata['flavor']].append(a)
                        else:
                            aggregate_classname[a.metadata['flavor']] = [a]

    flavor_classname = {}
    for f in my_flavs:
       if "flavor_class:name" in f.extra_specs.keys():
            if f.extra_specs['flavor_class:name'] in aggregate_classname.keys():
                if f.extra_specs['flavor_class:name'] in flavor_classname.keys():
                    flavor_classname[f.extra_specs['flavor_class:name']].append(f)
                else:
                    flavor_classname[f.extra_specs['flavor_class:name']] = [f]

    for cn in aggregate_classname.keys():
        for a in aggregate_classname[cn]:
            print("Aggregate:", a.name)
            print("Hosts:")
            for h in a.hosts:
                print("    ",h)
            print("Flavors:")
            if cn in flavor_classname.keys():
                for f in flavor_classname[cn]:
                    print("    ", f.name)
            print()

def flavor_unset(my_os_conn, my_flavor):
    """Unset all projects of a given flavor."""
#    flavors = nov.flavors.list(is_public=None)
    flavor = my_os_conn.get_flavor(my_flavor)
    fl_accas = my_os_conn.list_flavor_access(my_flavor)
    for fa in fl_accas:
        print(fa)
        print(fa['flavor_id'], fa['tenant_id'])


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


def allo_all_active(my_session):
    """Allocation report all active"""
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
    #print_structure_det(my_prj.data[0])

    print(" Project Name ", my_prj.data[0].name)
    print(" Project id ", my_prj.data[0].id)
    print(" Project allocation id ", my_prj.data[0].allocation_id)
    print(" Project tags ", my_prj.data[0].tags)

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
    print("quotas: ")
    for q in my_allo.quotas:
        print("  ",q.zone, q.resource, q.quota)

    #print(my_allo.quotas)
    print()
    print(my_allo)
    print_structure_det(my_allo)

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


def cin_metrics(my_session, host_name):
    cin_client = cin_cli.Client(version=3, session=my_session)
    avs = cin_client.availability_zones.list()
    print("zones")
    my_zones = []

    for a in avs:
        if 'elb' in a.zoneName:
            my_zones.append(a)

    my_hosts = []
    services = cin_client.services.list()
    for s in services:
        if s.binary == 'cinder-volume' and "elb" in s.zone:
            print(s.host, s)
            my_hosts.append(s.host)

#    pools = cin_client.pools.list()
#    for p in pools:
#        print(p)

    for host_name in my_hosts:
        print('Volumes in ', host_name)
        vols = cin_client.volumes.list(search_opts={'host': host_name, 'all_tenants': 1})
        total = 0
        for v in vols:
            # print(v.id, v.name, v.size,)
            total += v.size

        print(f'{total} GBs in host {host_name}')
        print('Number of Volumes', len(vols))
        print()


def main():
    """ CLI implementation temporal for fast trial while developing
    """
#p_volumes = os_conn.block_storage.volumes(all_projects=True,
#                                              project_id=project_id)  # Generator
    print(os.environ['OS_AUTH_URL'])
    print(os.environ['OS_USERNAME'])

    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    # Latest module
    os_conn = openstack.connect(cloud='envvars')

    # Create a keystone client interface
    # https://docs.openstack.org/python-keystoneclient/latest/api/keystoneclient.v3.html#module-keystoneclient.v3.client
    # ks_cli = ks_client.Client(session=my_session, include_metadata=True)

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

    # neu_cli.SessionClient(version=2, session=my_session)

    # ci_client = cin_cli.Client(version=3, session=my_session)

    ## works
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_det_basic('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_stop('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # server_status('7d55e9fe-ed55-43b0-93ef-b9d56bf30035', nv_client)
    # av_zone = input("av zone :")
    # server_list_per_az(av_zone, nv_client)

    print("(s) Servers, look for server names matching \n"
          "(sia) Server in an aggregate\n"
          "(sd) Server details by server id, all obj att \n"
          "(sip) Server by IP\n"
          "(p) Projects, look for project names matching \n"
          "(pd) prj det, show project details for the given project name \n"
          "(pbip) Project and Server Details by list of VM IPs ([ip1,ip2....]) \n"
          "(sp) Servers in Prj, for a given Prj-id\n"
          "(r) user role assignment, \n"
          "(ur) User resources, \n"
          "(f) Flavors, \n"
          "(fagr) Flavors on aggregates per availability zone, \n"
          "(fa) Flavor accessed by a Project-id, \n"
          "(fun) Flavor unset projects on a flavor \n"
          "(ai) allocation brief by allocation id\n"
          "(an) allocation brief by project name\n"
          "(ar) allocation report per site name\n"
          "(aa) allocation report per approver email\n"
          "(paz) projects per availability zone\n"
          "(pnd) project network details\n"
          "(sec) security groups per srv_id\n"
          "(lip) load balancers per ip\n")

    look_in = input(" your choice: ")
    look_for = input("Search for :")

    ips = [

    ]

    if look_in == "s":
        sleep(1)
    elif look_in == "sia":
        my_site = input("Site :")
        server_in_aggregate(os_conn, look_for, my_site)
    elif look_in == "sd":
        server_det_obj(look_for, nv_client)
    elif look_in == "sip":
        svr = server_by_ip(look_for, os_conn)
        print(svr)
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
    elif look_in == "fagr":  # flavor per aggregate
        flavor_aggregate(os_conn, look_for)
    elif look_in == "fa":  # Flavor Accessed by Project-id
        flavor_prjs(my_session, look_for)
    elif look_in == "fun":  # Flavor unset projects on flavor
        flavor_unset(os_conn, look_for)
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
    elif look_in == "pnd":  # Projects network details
        prj_net_det(os_conn, look_for)
    elif look_in == "sec": # security groups per svr_id
        sec_per_svrid(my_session, look_for)
    elif look_in =='cin':
        cin_metrics(my_session, look_for)
    elif look_in =='lip':
        ip_to_lb(os_conn, look_for)

    else:
        print("No option available")


if __name__ == '__main__':
    sys.exit(main())
