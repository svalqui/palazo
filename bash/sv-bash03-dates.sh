#!/usr/bin/env bash
#
#
# References
# https://stackoverflow.com/questions/27429653/date-comparison-in-bash
# https://stackoverflow.com/questions/9008824/how-do-i-get-the-difference-between-two-dates-under-bash
# https://phoenixnap.com/kb/bash-math
#
# Date today
echo "The date today, default: "
echo "    $(date)"
echo
# Date today in a given format
echo 'The date today, format +"%m-%d-%Y"'
echo "    $(date +"%m-%d-%Y")"
echo
# Show file stats
echo "Show file stats "
echo "file /etc/issue"
echo "$(stat /etc/issue)"
echo
# File last modified date
echo "file mod date: `stat -c%y /etc/issue`"
echo
# Days difference between file's mod date and today
my_file_date_sec=`stat -c%Y /etc/issue`
echo "file mod date, in seconds since epoch $my_file_date_sec"
echo
my_date_sec=$(date +%s)
echo "The date today, in seconds since 1970 "
echo "    $my_date_sec"
echo
let my_diff=($my_date_sec - $my_file_date_sec)/86400
echo "$my_diff days since file '/etc/issue' modification date and today"
echo
#
# Sort by date
for f in `find $HOME/ -maxdepth 1 -type f`
do
  stat -c '%Y %n' $f
#done | sort -n | cut -d ' ' -f2
done | sort -n
#
# Files older than a week
for f in `find $HOME/ -maxdepth 1 -mtime -7 -type f`
do
  echo "file $f newer than a week"
#done | sort -n | cut -d ' ' -f2
done | sort -n
echo
#
# Pretent delete older files
# deleting older files of a given name
while (ls $HOME/python3* | wc -l > 2 ) # If there are more than 2
do
  echo "$(ls -t $HOME/python3* | tail -1)" # Delete the older first
  break
done




