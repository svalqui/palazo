#!/usr/bin/env bash
#
#
# References
# https://www.cyberciti.biz/faq/bash-for-loop-array/
#
# Users
USERS=("ab" "bc" "cd")

echo

# Create a string from the array separate by commas
L_U=$( IFS=$','; echo "${USERS[*]}")
echo "$L_U"

echo

# Replace comma on string by comma and space
L_2=$(echo "$L_U" | sed -r 's/,/, /g')
echo "$L_2"

# Show the elements of the array
for u in "${USERS[@]}";
do
    echo $u
done

echo
echo "Or..."
echo

# Show key-value of array
for key in "${!USERS[@]}"
do
    echo "Key...'$key' Value...'${USERS[$key]}'"
done
