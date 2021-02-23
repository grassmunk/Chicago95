#!/bin/bash

# Generates HTML to show a preview of all icons in a given folder
# Part of the Chicago95 project

icons=$(find|awk -F'/' '{print $3}'|sed 's/\.[^.]*$//'|sort|uniq)
dirs=$(find -mindepth 1 -type d|sort -V|grep -v 256)
size=$(wc -w <<< "$dirs")

cat << HERE
<!DOCTYPE html>
<html>
<head>
<style>
td {
  border: 1px solid black;
  padding: 10px;
  text-align:center;
  font-size: x-small;
  vertical-align: bottom;
  background: white;
}
table {
  position: relative;
  margin-left: auto;
  margin-right: auto;
}

th {
  background: #000080;
  color: white;
  position: sticky;
  top: 0;
  border: 1px solid black;
  padding: 10px;
  text-align:center;
}

body {
  background: #008080;
  font-family: Arial, Helvetica, Arial, sans-serif;
}
h1, h2 {
  font-family: Arial, Helvetica, Arial, sans-serif;
  color: white;
  text-align:center;
  font-weight: bold;
}
</style>
<title>Chicago 95 Icons: ${PWD##*/}</title>
<!-- Part of the Chicago95 project -->
</head>
<body><h1>Chicago95 Icons: ${PWD##*/}</h1>
<br><br>
<p style="color:white">Below is the list of all icons using in the <b>${PWD##*/}</b> section. Each icon is identified by its name. If the icon is a symlink to another icon it will be followed by the name of the link target.</p>
<br><br>
<table>
HERE


echo -e "\t<tr>"
for d in $dirs; do
    echo -e "\t\t<th>${d##*/}</th>"
done
echo -e "\t</tr>"

for i in $icons; do
    filename=$i
    echo -e "\t<tr>"
    for d in $dirs; do
        echo -e "\t\t<td>"
        if [ $d = "./scalable" ]; then
            checkfile="$filename.svg"
            img=$(echo "<img width=48px src=\"$d/$checkfile\" alt=\"$checkfile\"></img>")
        else
            checkfile="$filename.png"
            img=$(echo "<img src=\"$d/$checkfile\" alt=\"$checkfile\"></img>")
        fi
        if [ -f "$d/$checkfile" ]; then
            echo -e "\t\t\t$img"
            echo -e "\t\t\t<br>$checkfile"
        fi
        if [ -L "$d/$checkfile" ]; then
            realfile=$(readlink -f $d/$checkfile)
            echo -e "\t\t\t<br>(<b>$(basename $realfile)</b>)"
        fi
        echo -e "\t\t</td>"
    done
    echo -e "\t</tr>"
done

echo -e "</table></body></html>"