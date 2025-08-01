#!/usr/bin/env bash
# bash/sv-bash07-arg-if.sh a b c d

echo number of arguments $#
echo all arguments $@
c=0
for arg in $@
  do
    let c++
    echo arg $c is $arg
  done

if [ $# -eq 2 ]
then
  echo has 2 arguments, second argument is $2
fi




