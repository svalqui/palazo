a=0
b=false

echo "$a"
echo "$b"


while [ "$a" -lt 100 ] &  [ "$b" == "false" ] ; do
  echo "$a"
  a=$((a+2))
  if [ "$a" == 10 ] ; then
    b=true
  fi;
done
  
