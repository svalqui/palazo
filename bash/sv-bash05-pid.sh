#!/usr/bin/env bash
#
ps -ef | while read line
do 
  my_pid=$(echo $line | cut -d' ' -f2) 
  echo $my_pid 
done
