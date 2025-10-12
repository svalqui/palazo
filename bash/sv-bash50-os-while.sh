#!/bin/bash

hosts_path="/tmp/hosts_$(date +"%Y-%m-%d-%H-%M-%S")"

openstack server list --host $1 --all-projects  | grep -e ACTIVE  | cut -f2 -d' ' > "$hosts_path"

no_of_vms=$(cat < "$hosts_path" | wc -l)
echo "number of VMs $no_of_vms"
shown=0

while  IFS= read -r vm  && [ "$no_of_vms" -ne "$shown" ]  ; do
  echo " vm $vm"
  shown=$((shown+1))
  echo "    shown $shown"

done < <(cat $hosts_path)

