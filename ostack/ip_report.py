import os
import sys
import time

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keys_client

from novaclient import client as nova_cli
from nectarallocationclient import client as allo_client
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
    """ Report VMs, IP
    """
    av_zone = input("Availability_zone :")

    # Authenticate using environmental variables
    my_session = os_auth_env_sess()

    nv_client = nova_cli.Client(version=2, session=my_session)
    ks_client = keys_client.Client(session=my_session, include_metadata=True)
    al_client = allo_client.Client(version=1, session=my_session)

    # print("Getting availability zones")
    av_zones = nv_client.availability_zones.list()

    # print("Getting users")
    users = ks_client.users.list()
    # list of users on users.data

    # index users by user.id
    users_dict = {}
    for user in users.data:
        users_dict[user.id] = user

    # print("Getting the projects")
    projects = ks_client.projects.list()
    # list of projects on projects.data

    # index projects by project.id
    projects_dict = {}
    for project in projects.data:
        projects_dict[project.id] = project

    # print("Getting the allocations")
    allocations = al_client.allocations.list()

    # index allocations by allocation id
    allocations_dict = {}
    for allocation in allocations:
        allocations_dict[allocation.id] = allocation

    total = 0
    for zone in av_zones:
        if zone.zoneName == av_zone:
            if zone.hosts:
                for my_host in zone.hosts.keys():
                    # print("Getting Servers of ", my_host)
                    servers = nv_client.servers.list(search_opts={'host': my_host, 'all_tenants': 1})
                    for server in servers:
                        # Cosmetics, make addresses pretty
                        server_add = ""
                        if server.addresses:
                            for key in server.addresses.keys():
                                server_add += key + ' '
                                for item in server.addresses[key]:
                                    server_add += item['addr'] + '; '

                        # Contact details
                        contact_e = ""
                        if hasattr(projects_dict[server.tenant_id], 'allocation_id'):
                            if projects_dict[server.tenant_id].allocation_id == "":  # if allocation_id is empty
                                contact_e = users_dict[server.user_id].email + users_dict[server.user_id].full_name
                            elif projects_dict[server.tenant_id].allocation_id == 59457:  # if is RPS Instant Dashboard
                                contact_e = "rcs-info@unimelb.edu.au"
                            else:  # if it has allocation id get the contact details from the allocation
                                contact_e = allocations_dict[
                                    projects_dict[server.tenant_id].allocation_id].contact_email

                        else:  # if no allocation get the email from the user details
                            if hasattr(users_dict[server.user_id], 'email'):
                                contact_e = users_dict[server.user_id].email
                            if hasattr(users_dict[server.user_id], 'full_name'):
                                contact_e += " " + users_dict[server.user_id].full_name
                            else:
                                contact_e = server.user_id

                        print( my_host, ", ",
                               server.id, ", ",
                               server.name, ", ",
                               server_add, ", ",
                               projects_dict[server.tenant_id].name, ", ",
                               projects_dict[server.tenant_id].description, ", ",
                               contact_e, ", ",
                               )
                    print(len(servers))
                    total += len(servers)

    print(total)

if __name__ == '__main__':
    sys.exit(main())

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

## Server
# Attributes:
# OS-DCF:diskConfig str
# OS-EXT-AZ:availability_zone str
# OS-EXT-SRV-ATTR:host None NoneType
# OS-EXT-SRV-ATTR:hypervisor_hostname None NoneType
# OS-EXT-SRV-ATTR:instance_name  str
# OS-EXT-STS:power_state 0 int
# OS-EXT-STS:task_state str
# OS-EXT-STS:vm_state str
# OS-SRV-USG:launched_at None NoneType
# OS-SRV-USG:terminated_at None NoneType
# accessIPv4  str
# accessIPv6  str
# addresses {} dict
# config_drive  str
# created  str
# flavor {} dict
# hostId  str
# human_id  str
# id  str
# image {} dict
# key_name str
# links [] list
# metadata {} dict
# name  str
# networks OrderedDict() OrderedDict
# os-extended-volumes:volumes_attached [] list
# progress 0 int
# request_ids [] list
# security_groups [] list
# status BUILD str
# tenant_id  str
# updated str
# user_id str
# x_openstack_request_ids [] list
