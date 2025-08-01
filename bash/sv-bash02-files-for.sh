#!/usr/bin/env bash
#
# References
# https://askubuntu.com/questions/605411/difference-between-and-in-bash
# https://stackoverflow.com/questions/2437452/how-to-get-the-list-of-files-in-a-directory-in-a-shell-script
# https://stackoverflow.com/questions/26575507/sort-list-of-files-by-date-in-bash
#
#
echo  "List files in directory"
#
# Using a variable 
dir=/etc/sysstat/*

for entry in $dir
do
  echo "File full path: $entry"
  echo "File name:  $(basename "$entry")"
done
echo

# Show file stats
echo "Show file stats "
echo "file /etc/issue"
echo "$(stat /etc/issue)"
echo
echo "file mod date: `stat -c%y /etc/issue`"
echo
#
# Using find
for FILE in `find /dev/tty2* -type c`
do
  echo "$FILE"
done
echo
#
# Using a directory and wildcard
for entry in /dev/tty2*
do 
  echo "$entry"
done
echo
#
# Sort by date
for f in "$HOME/*" 
do
  stat -c '%Y %n' $f
done | sort -n | cut -d ' ' -f2
