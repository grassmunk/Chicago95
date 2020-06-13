#!/bin/bash

rm new_missing

for i in `cat elementary2.txt`; do
echo $i
if test -f "$i"; then
  echo "$i exists"
  cp -P --parent $i ../../Chicago95/
else
  echo $i >> new_missing
  echo "$i does not exists"
fi
done

