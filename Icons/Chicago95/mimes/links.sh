#!/bin/bash

for i in `find . -type l`
do 
	newfile=`echo $i|sed 'p;s/\.png/\.svg/'|grep "\.svg"` 
	target=`ls -l $i|awk '{print $11}'|sed 'p;s/\.png/\.svg/'|grep "\.svg"`
	echo "Newfile: $newfile"
	echo "Target: $target"
        ln -s $target $newfile
       	rm $i
done
