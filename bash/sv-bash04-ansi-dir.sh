#!/usr/bin/env bash
touch site.yml
mkdir host_vars
mkdir groups_vars
mkdir -p roles/{common, my_services1}/{tasks,handlers,files,templates,vars,default,meta}
