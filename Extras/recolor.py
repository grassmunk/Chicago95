#!/usr/bin/env python3
#requires python-pil

import shutil
import os
from PIL import Image
p = os.path.join

#config
inPath = os.path.expanduser("~/.themes/Chicago95")
outPath = os.path.expanduser("~/.themes/Chicago95.custom")

#set the colors you want to change here (this example mimics w2000):
remapColors = {
	"#000080": "#0a246a",	#main blue
	"#dfdfdf": "#dfdfdf",	#highlight
	"#c0c0c0": "#d4cfc7",	#main window color
	"#ffffff": "#ffffff",	#main window color inner
	"#808080": "#808080",	#shadow 1
	"#000000": "#000000"	#shadow 2
}
#config end

def hexToRGB(h):
	h = h.replace("#","")
	return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgbaToRGB(tup):
	return (tup[0],tup[1],tup[2])

if (os.path.isdir(outPath)):
	shutil.rmtree(outPath)

os.makedirs(outPath)

for root,dirs,files in os.walk(inPath):
	for dir in dirs:
		fpath = p(root,dir)
		nfpath = fpath.replace(inPath,outPath)
		if not (os.path.isdir(nfpath)):
			os.makedirs(nfpath)
	
	for file in files:
		fpath = p(root,file)
		nfpath = fpath.replace(inPath,outPath)
		lpath = fpath.replace(inPath + "/","")
		ext = os.path.splitext(fpath)[1].lower()
		
		if (ext == ".css") or (ext == ".scss") or (ext == ".xpm") or (ext == ".svg") or (ext == ".rc")\
		or (lpath == "gtk-2.0/gtkrc") or (lpath == "xfwm4/hidpi/themerc") or (lpath == "xfwm4/themerc"):
			print("editing text: " +fpath)
			fileh = open(fpath,"r")
			nfileh = open(nfpath,"w")
			for line in fileh:
				for color in remapColors:
					colorV = remapColors[color]
					line = line.replace(color.upper(),colorV.upper())
					line = line.replace(color.lower(),colorV.lower())
				
				nfileh.write(line)
			
			fileh.close()
			nfileh.close()
		
		if (ext == ".png"):
			print("editing image: " +fpath)
			img = Image.open(fpath)
			img = img.convert("RGBA")
			pixels = img.load()
			width, height = img.size
			for y in range(height):
				for x in range(width):
					pixel = pixels[x,y]
					for color in remapColors:
						colorV = remapColors[color]
						rgbColor = hexToRGB(color)
						rgbColorV = hexToRGB(colorV)
						if (rgbaToRGB(pixel) == rgbColor):
							pixels[x,y] = (rgbColorV[0],rgbColorV[1],rgbColorV[2],pixel[3])
							break
			
			img.save(nfpath)
			img.close()
		
		if not (os.path.isfile(nfpath)):
			shutil.copy(fpath,nfpath)
