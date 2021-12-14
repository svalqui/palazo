# Copyright 2021 by Sergio Valqui. All rights reserved.

import pathlib
import sys
import os

import novaclient
from novaclient import client as nova_client
from cinderclient import client as cinder_client
from time import sleep
import platform
import subprocess
import argparse
import configparser

# Session Authentication
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


def session_env_var():
    """Authenticates using environmental variables and returns a session-token.
    https://docs.openstack.org/python-keystoneclient/latest/using-api-v3.html
    """
    auth = v3.Password(auth_url=os.environ['OS_AUTH_URL'],
                       user_id=os.environ['OS_USERNAME'],
                       password=os.environ['OS_PASSWORD'],
                       project_id=os.environ['OS_PROJECT_ID'])
    os_session = session.Session(auth=auth)
    print(os_session)
    ks = ks_client.Client(session=os_session)
    users = ks.users.list()
    print("users length ", len(users))
    for i in users:
        print(i)

    return os_session


def main():
    """ CLI implementation temporal for fast trial while developing
    it requires palazo.ini 2 directories up with configuration as follow
    --- palazo.ini ---
    [openstack]
    OS_AUTH_URL=https://
    OS_PROJECT_ID=
    OS_PROJECT_NAME=
    OS_USERNAME="username@domain.org"
    OS_PASSWORD=
    OS_REGION_NAME="Melbourne"
    --- end of palazo.ini ---
    :return:
    """

#     # Removing configuration from Project, configuration file 'palazo.ini' moved 2 directories up
#     file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
#     print('file_conf_dir', file_conf_dir)
#     file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
#     print('file_conf_name', file_conf_name)
#
#     # Reading configuration
#     config = configparser.ConfigParser()
#
#     # Get project site and authentication credentials
#     try:
#         config.read(str(file_conf_name))
#         os_user_name = config['openstack']['OS_USERNAME']
#         print(os_user_name)
#         os_user_pass = config['openstack']['OS_PASSWORD']
#         os_version = config['openstack']['OS_API_VERSION']
#         os_project_id = config['openstack']['OS_PROJECT_ID']
#         os_project_name = config['openstack']['OS_PROJECT_NAME']
#         os_auth_url = config['openstack']['OS_AUTH_URL']
#         os_user_domain = config['openstack']['OS_USER_DOMAIN_NAME']
#
#         proceed = True
#
#     except BaseException as e:
#         print('--FileError: ', e)
#         print('--Exception Name :', type(e))
#         proceed = False
#
#     if proceed:
#         nova = client.Client(version=os_version, username=os_user_name, password=os_user_pass,
#                              project_id=os_project_id, auth_url=os_auth_url, user_domain_name=os_user_domain)
#
#         cinder = cinder_client.Client(version=3, username=os_user_name, api_key=os_user_pass,
#                                       project_id=os_project_name, auth_url=os_auth_url)
#
#         imas = nova.glance.list()
#         vols = cinder.volumes.list()
#         flavs = nova.flavors.list()
#
#         # print_structure(nova.servers))
#         # print()
#
#         # print(dir(cinder.volumes))
#         # print()
#         # print(dir(cinder.volumes.list()[0]))
#         # print()
# # # nova structure
# #         print(dir(nova))
# #         print()
# # # servers structure
# #         print(dir(nova.servers))
# #         print()
# # # images structure
# #         print(dir(nova.glance))
# #         print()
# #         print(nova.glance.list())
# #         print()
# #         print(dir(nova.glance.list()[0]))
# #         print()
# #         print(nova.glance.list()[0].name)
# # # a server structure
# #         print(dir(l[0]))
# #         print()
# # # addresses, a server has a list of ip adds
# #         print(dir(l[0].addresses))
# #         print()
# # # server properties
# #         print(l[0].name)
# #         print(l[0].image)
# #         print()
#
#         i_ip = ''
#         # for i in imas:
#         #     print(i, i.id, i.name)
#         for instance in nova.servers.list():
#             i_image_name = ''
#             # get instance name
#             i_name = instance.name
#             # get IP address  TODO get ip address from other attribute  'accessIPv4'
#             for net in instance.addresses.keys():  # Str
#                 for ip_list in instance.addresses[net]:  # list
#                     i_ip += ip_list['addr'] + ' '
#             # get image name
#             i_image = str(instance.image)
#             if i_image == '':  # N/A (booted from volume) no image info on instance but on volume
#                 # id of the first volume, os-extended-volumes:volumes_attached returns a list of volumes
#                 i_first_volume_id = getattr(instance, "os-extended-volumes:volumes_attached")[0]['id']
#                 i_first_vol = cinder.volumes.get(i_first_volume_id)
#                 i_image_name = i_first_vol.volume_image_metadata['image_name']
#             else:  # Has an image
#                 # id of the image
#                 i_image_id = instance.image['id']
#                 try:
#                     ima = nova.glance.find_image(instance.image['id'])
#                     i_image_name = ima.name
#                 except novaclient.exceptions.NotFound:
#                     i_image_name = "Img no longer available"
#                 except Exception as e:
#                     print(e)
#             # get flavor name
#             i_flavor = nova.flavors.get(instance.flavor['id'])
#             i_flavor_name = i_flavor.name
#             # get description
#             # i_des = instance.description
#             i_des = ''
#
#             line = i_name + ' ' + i_ip + ' ' + i_image_name + ' ' + i_flavor_name + ' ' + i_des
#             i_ip = ''
#             i_image_name = ''
#             i_flavor = ''
#             print(line)

    session_env_var()

if __name__ == '__main__':
    sys.exit(main())




