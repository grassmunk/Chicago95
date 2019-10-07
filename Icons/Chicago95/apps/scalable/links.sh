#!/bin/bash
rm *.svg
rm *.png
cp -avn ../48/* ./
cp -avn ../32/* ./

echo "[+] Generating SVGs"

for i in `find ./ -type f|grep -i "\.png"`
do 
	pixel2svg.py --squaresize=20 $i
	rm $i
done

echo "[+] Making links"

for i in `find . -type l`
do 
	newfile=`echo $i|sed 'p;s/\.png/\.svg/'|grep "\.svg"` 
	target=`ls -l $i|awk '{print $11}'|sed 'p;s/\.png/\.svg/'|grep "\.svg"`
	echo "Newfile: $newfile"
	echo "Target: $target"
        ln -s $target $newfile
       	rm $i
done

