# Copyright 2021 by Sergio Valqui. All rights reserved.
# based on launch.py by Jinyuan Chen (jinyuanc1@unimelb.edu.au)

import pathlib
import sys

import novaclient
from novaclient import client
from cinderclient import client as cinder_client
from time import sleep
import platform
import subprocess
import argparse
import configparser


def look_for_obj_by_att_val(my_obj_list, my_att, my_value):

    ret_obj = None
    for my_obj in my_obj_list:
        if my_att in dir(my_obj):
            # print(getattr(my_obj, my_att), my_value)
            if getattr(my_obj, my_att) == my_value:
                ret_obj = my_obj
                break
    return ret_obj


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

    # Removing configuration from Project, configuration file 'palazo.ini' moved 2 directories up
    file_conf_dir = pathlib.Path(__file__).absolute().parents[2]
    print('file_conf_dir', file_conf_dir)
    file_conf_name = pathlib.Path(file_conf_dir) / 'palazo.ini'
    print('file_conf_name', file_conf_name)

    # Reading configuration
    config = configparser.ConfigParser()

    try:
        config.read(str(file_conf_name))
        os_user_name = config['openstack']['OS_USERNAME']
        print(os_user_name)
        os_user_pass = config['openstack']['OS_PASSWORD']
        os_version = config['openstack']['OS_API_VERSION']
        os_project_id = config['openstack']['OS_PROJECT_ID']
        os_project_name = config['openstack']['OS_PROJECT_NAME']
        os_auth_url = config['openstack']['OS_AUTH_URL']
        os_user_domain = config['openstack']['OS_USER_DOMAIN_NAME']

        proceed = True

    except BaseException as e:
        print('--FileError: ', e)
        print('--Exception Name :', type(e))
        proceed = False

    if proceed:
        nova = client.Client(version=os_version, username=os_user_name, password=os_user_pass,
                             project_id=os_project_id, auth_url=os_auth_url, user_domain_name=os_user_domain)

        cinder = cinder_client.Client(version=os_version, username=os_user_name, api_key=os_user_pass,
                                      project_id=os_project_name, auth_url=os_auth_url)

        l = nova.servers.list()
        imas = nova.glance.list()
        vols = cinder.volumes.list()

        # print(dir(cinder.volumes))
        # print()
        # print(dir(cinder.volumes.list()[0]))
        # print()
# # nova structure
#         print(dir(nova))
#         print()
# # servers structure
#         print(dir(nova.servers))
#         print()
# # images structure
#         print(dir(nova.glance))
#         print()
#         print(nova.glance.list())
#         print()
#         print(dir(nova.glance.list()[0]))
#         print()
#         print(nova.glance.list()[0].name)
# # a server structure
#         print(dir(l[0]))
#         print()
# # addresses, a server has a list of ip adds
#         print(dir(l[0].addresses))
#         print()
# # server properties
#         print(l[0].name)
#         print(l[0].image)
#         print()
        i_name = ''
        i_ip = ''
        i_image = ''
        i_flavor = ''
        line = ''
        # for i in imas:
        #     print(i, i.id, i.name)
        for instance in nova.servers.list():
            i_name = instance.name
            #print("Ins :", i_name)
            # find IP fromm networks
            for net in instance.addresses.keys():  # Str
                for ip_list in instance.addresses[net]:  # list
                    i_ip += ip_list['addr'] + ' '
            i_image = str(instance.image)
            # print("Ima :", i_image)
            # for item in dir(instance):
            #     print(item, getattr(instance, item), type(getattr(instance, item)).__name__)
            if i_image == '':  # N/A (booted from volume)
                # id of the first volume, os-extended-volumes:volumes_attached returns a list of volumes
                i_first_volume_id = getattr(instance, "os-extended-volumes:volumes_attached")[0]['id']
                i_first_vol = cinder.volumes.get(i_first_volume_id)
                i_image_name = i_first_vol.volume_image_metadata['image_name']
            else:  # Has an image
                # id of the image
                i_image_id = instance.image['id']
                ima = look_for_obj_by_att_val(imas, 'id', i_image_id)
                if ima is not None:  # image on nova.glance.list()
                    i_image_name = ima.name
                else:  # no image on nova.glance.list()
                    try:
                        ima = nova.glance.find_image(instance.image['id'])
                        i_image_name = ima.name
                    except novaclient.exceptions.NotFound:
                        i_image_name = "Img no longer available"
                        print()
                    except Exception as e:
                        print(e)
            line = i_name + ' ' + i_ip + ' ' + i_image_name
            i_ip = ''
            i_image_name = ''
            print(line)


if __name__ == '__main__':
    sys.exit(main())




