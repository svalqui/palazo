#!/usr/bin/env bash
#
#
# References
# https://askubuntu.com/questions/605411/difference-between-and-in-basha
# https://www.gnu.org/software/bash/manual/bash.html#Shell-Parameter-Expansion
echo "' everything between single quotes is presente literally"
echo '    like this...'
echo
echo "\" everything between double quotes executes shell expansions"
echo
echo '    with single quotes'
echo '    $HOME'
echo '    $(date)'
echo
echo '    with double quotes'
echo "    $HOME"
echo "    $(date)"
echo
echo '` grave accent as $() is used to execute commands'
echo '    with single quotes'
echo '    `whoami`'
echo '    $(lscpu | grep "Model name")'
echo
echo '    with double quotes and grave accent'
echo "    `whoami`"
echo "    $(lscpu | grep "Model name")"
echo

