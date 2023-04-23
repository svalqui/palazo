#!/usr/bin/env bash
#
#
# References
# https://stackoverflow.com/questions/27429653/date-comparison-in-bash
# https://stackoverflow.com/questions/9008824/how-do-i-get-the-difference-between-two-dates-under-bash
# https://phoenixnap.com/kb/bash-math
#
echo "The date today, default: "
echo "    $(date)"
echo
echo 'The date today, format +"%m-%d-%Y"'
echo "    $(date +"%m-%d-%Y")"
echo
# Show file stats
echo "Show file stats "
echo "file /etc/issue"
echo "$(stat /etc/issue)"
echo
echo "file mod date: `stat -c%y /etc/issue`"
echo
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
