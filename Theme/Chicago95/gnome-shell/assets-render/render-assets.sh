#! /bin/bash

INKSCAPE="/usr/bin/inkscape"
OPTIPNG="/usr/bin/optipng"
ASSETS_DIR="assets"

for i in *.svg
do
  extension="${i##*.}"
  name=${i%".$extension"}

  if [ -f $ASSETS_DIR/$name.png ]; then
    echo $ASSETS_DIR/$name.png exists.
  else
    echo
    echo Rendering $ASSETS_DIR/$name.png
    
    $INKSCAPE --export-png=$ASSETS_DIR/$name.png $i >/dev/null \
    && $OPTIPNG -o7 --quiet $ASSETS_DIR/$name.png 
  fi
  
  if [ -f $ASSETS_DIR/$name@2.png ]; then
    echo $ASSETS_DIR/$name@2.png exists.
  else
    echo
    echo Rendering $ASSETS_DIR/$name.png
    
    $INKSCAPE --export-dpi=180 \
              --export-png=$ASSETS_DIR/$name@2.png $i >/dev/null \
    && $OPTIPNG -o7 --quiet $ASSETS_DIR/$name@2.png 
  fi
done
