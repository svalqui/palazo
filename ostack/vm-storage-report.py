#!/usr/bin/env python

import openstack

from os import path
import sys

sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def main():
    """ OS VM Report
    """

    print("Connecting...")
    os_conn = openstack.connect(cloud='envvars')

    print("Getting Hypervisors...")
    hypervisors = os_conn.compute.hypervisors()
 #   projects = list(os_conn.identity.projects(limit=10000))
 #   print("projects", len(projects))
    projects_dict = {}

    total_vms = 0
    total_hypervisors = 0

    for hypervisor in hypervisors:
        if "qh2-rc" in hypervisor.name:
            total_hypervisors += 1
            print(f"\nHypervisor: {hypervisor.name}, State: {hypervisor.state}, Status: {hypervisor.status}")
            # Get VMs on this hypervisor
            hostname = hypervisor.name.partition('.')[0]
            vms = os_conn.list_servers(all_projects=True, filters={'compute_host': hostname})

            print(f"  VMs running: {len(vms)}")
            total_vms += len(vms)
            for vm in vms:
                got_image = False
                got_volume = False

                #print(vm)
                #print(dir(vm))

                if vm.project_id in projects_dict:
                    prj_name = projects_dict[vm.project_id].name
                else:
                    project = os_conn.get_project(vm.project_id)
                    projects_dict[vm.project_id] = project
                    prj_name = project.name

                locked_compose = ""
                if vm.is_locked:
                    locked_compose = "LOCKED " + vm.locked_reason

                print(f"    {vm.id}, {vm.name[0:20]}, {prj_name[0:20]}, Status: {vm.status}, {locked_compose}")
                if vm.image:
                    print(f"        Image ID: {vm.image.id}, Name: {vm.image.name}")
                    got_image = True
                if vm.attached_volumes :
                    # details are in the volume attachments
                    attachments = os_conn.compute.volume_attachments(vm.id)
                    for att in attachments:
                        #print(att)
                        # print(dir(att))
                        # print("    Volume: ", att['device'], att['volume_id'], att['attachment_id'])
                        volume = os_conn.get_volume(att.volume_id)

                        line = f"        {att.device}, {att.server_id}, {att.volume_id}, {att.attachment_id}, {att.bdm_id}, {volume.cluster_name}"
                        print(line)


                    #print("VM id: ", vm.id)
                    #print("Attached Volumes:")
                    #print(vm.attached_volumes)
                    # details are in the volume attachments
                    # or in the volume attachments=[{
                    #for att_vol in vm.attached_volumes:
                    #    #print(att_vol)
                    #    #print(dir(att_vol))
                    #    #print("    ", att_vol.id, att_vol.volume_id)
                    #    vol = os_conn.block_storage.get_volume(att_vol.id)
                    #    #print("---")
                    #    #print(vol)
                    #    #print(dir(vol))
                    #    print(vol.attachments)
                    #    #print(vol.attachments[0])
                    #    #print("====")
                    #    # print("    Volume: ", att['device'], att['volume_id'], att['attachment_id'])
                    #    print("    ",
                    #          vol.attachments[0]['device'],
                    #          vol.attachments[0]['server_id'],
                    #          vol.attachments[0]['volume_id'],
                    #          vol.name[0:20],
                    #          vol.attachments[0]['id'],
                    #          vol.cluster_name
                    #          )

                    got_volume = True

                if got_volume and got_image:
                    print("    *** Got both image and attached volumes")

    print(f"\nTotal Hypervisors: {total_hypervisors}")
    print(f"\nTotal VMs: {total_vms}")

if __name__ == '__main__':
    sys.exit(main())




