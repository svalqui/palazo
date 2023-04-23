#!/usr/bin/env bash
#
#
# References
# https://askubuntu.com/questions/605411/difference-between-and-in-bash
# https://stackoverflow.com/questions/2437452/how-to-get-the-list-of-files-in-a-directory-in-a-shell-script
#
echo  "List files in directory"
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

for FILE in `find /dev/tty2* -type c`
do
  echo "$FILE"
done
