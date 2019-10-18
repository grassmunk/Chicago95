#!/usr/bin/python3
# -*- coding: utf-8 -*- 

# Tool to parse and generate new Chicago95 themes based on Microsoft Theme files
# Parses ANI and ICO files, installs Icons/Theme and fonts
# Auto changes your theme
# Thanks to png2svg for icon converter and Fierelier for recoloring script
# Requires:
# - Inkscape
# - Imagemagick
# - xcursorgen
# - Chicago95 icons, theme and cursors installed
# TODO:
# - Add sound support
# - Add better themeing color support
# - Add a gui
# - Better font identification

import sys
import os
import collections
import PIL.Image
import svgwrite
import pathlib
import shutil
import subprocess
import argparse
import logging
import configparser
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
from configparser import ConfigParser

plus = '''
 ██████╗██╗  ██╗██╗ ██████╗ █████╗  ██████╗  ██████╗  █████╗ ███████╗
██╔════╝██║  ██║██║██╔════╝██╔══██╗██╔════╝ ██╔═══██╗██╔══██╗██╔════╝
██║     ███████║██║██║     ███████║██║  ███╗██║   ██║╚██████║███████╗
██║     ██╔══██║██║██║     ██╔══██║██║   ██║██║   ██║ ╚═══██║╚════██║
╚██████╗██║  ██║██║╚██████╗██║  ██║╚██████╔╝╚██████╔╝ █████╔╝███████║
 ╚═════╝╚═╝  ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝  ╚════╝ ╚══════╝
								                     ___   
							.---.                     .'/   \  
				_________   _...._      |   |                    / /     \ 
				\        |.'      '-.   |   |                    | |     | 
				 \        .'```'.    '. |   |                    | |     | 
				  \      |       \     \|   |                    |/`.   .' 
				   |     |        |    ||   |   _    _         _  `.|   |  
				   |      \      /    . |   |  | '  / |      .' |  ||___|  
				   |     |\`'-.-'   .'  |   | .' | .' |     .   | /|/___/  
				   |     | '-....-'`    |   | /  | /  |   .'.'| |//.'.--.  
				  .'     '.             '---'|   `'.  | .'.'.-'  /| |    | 
				'-----------'                '   .'|  '/.'   \_.' \_\    / 
							      `-'  `--'            `''--'  '''


def hexToRGB(h):
	return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgbaToRGB(tup):
	return (tup[0],tup[1],tup[2])

def convert_icon_files(icon_filename, output_file_name):
	convert_path = subprocess.check_output(["which", "convert"]).strip()
	logging.info("\t{:<21} {}".format(os.path.split(icon_filename)[1], os.path.split(output_file_name)[1]))
	args = [
	convert_path,
	icon_filename,
	output_file_name
	]
	subprocess.check_call(args)
	if  os.path.isfile(output_file_name[:-4]+"-0.png"):
		shutil.move(output_file_name[:-4]+"-0.png", output_file_name[:-4]+".png")

def make_x11_cursors(icons_file, seq=False, rate=False, in_filename="tmp_file", out_folder="tmp_file.png"):
	logging.debug("[x11_cursors]")
	icon_num = 1
	icon_file_names = []
	for icon in icons_file:
		if len(icon) == 0:
			# Skip empty icons
			continue
		icon_type = int.from_bytes(icon[2:4],"little")
		number_of_images = int.from_bytes(icon[4:6],"little")
		if icon_type == 1:
			ext = ".ico"
		else:
			ext = ".cur"
		
		path_to_ani, ani_file_name = os.path.split(in_filename)
		icon_name = os.path.splitext(ani_file_name)[0].replace(" ","_")		
		
		if seq:
			num = "_{:02}".format(seq[icon_num-1])
		else:
			num = "_{:02}".format(icon_num)

		if rate and type(rate) is list:
			jif = "_{}".format(rate[icon_num-1])
		elif rate:
			jif = "_{}".format(rate)
		else:
			jif = "_{}".format(10)

		icon_file = icon_name + jif + num + ext
		logging.debug("\t{:<21} {}".format(icon_file, out_folder))

		icon_num += 1
		
		icon_file_names.append(out_folder+icon_file)
		f = open(out_folder+icon_file,"wb")
		f.write(icon)
		f.close()
	return icon_file_names

def build_cursors(cursor_folder):

	#xcursors defs
	xcursors_conf = {
	"01_AngleNW.conf"	:	"ul_angle",
	"02_AngleNW.conf"	:	"dnd-none",
	"03_AngleNW.conf"	:	"dnd-move",
	"04_AngleNE.conf"	:	"ur_angle",
	"05_AngleNE.conf"	:	"ll_angle",
	"06_AngleNW.conf"	:	"lr_angle",
	"07_AppStarting.conf"	:	"left_ptr_watch",
	"08_AppStarting.conf"	:	"08e8e1c95fe2fc01f976f1e063a24ccd",
	"09_AppStarting.conf"	:	"3ecb610c1bf2410f44200f48c40d3599",
	"10_Arrow.conf"	:	"arrow",
	"11_Arrow.conf"	:	"draft_large",
	"12_Arrow.conf"	:	"draft_small",
	"13_Arrow.conf"	:	"left_ptr",
	"14_Arrow.conf"	:	"right_ptr",
	"15_Arrow.conf"	:	"top_left_arrow",
	"16_ArrowRight.conf"	:	"right_ptr",
	"17_BaseN.conf"	:	"base_arrow_up",
	"18_BaseN.conf"	:	"based_arrow_up",
	"19_BaseN.conf"	:	"base_arrow_down",
	"20_BaseN.conf"	:	"based_arrow_down",
	"21_Circle.conf"	:	"circle",
	"22_Copy.conf"	:	"copy",
	"23_Copy.conf"	:	"1081e37283d90000800003c07f3ef6bf",
	"24_Copy.conf"	:	"6407b0e94181790501fd1e167b474872",
	"25_Copy.conf"	:	"08ffe1cb5fe6fc01f906f1c063814ccf",
	"26_Cross.conf"	:	"cross",
	"27_Cross.conf"	:	"cross_reverse",
	"28_Cross.conf"	:	"tcross",
	"29_Crosshair.conf"	:	"crosshair",
	"30_DND-ask.conf"	:	"dnd-ask",
	"31_DND-copy.conf"	:	"dnd-copy",
	"32_DND-link.conf"	:	"dnd-link",
	"33_Hand.conf"	:	"hand",
	"34_Hand.conf"	:	"hand1",
	"35_Hand.conf"	:	"hand2",
	"36_Hand.conf"	:	"e29285e634086352946a0e7090d73106",
	"37_Handgrab.conf"	:	"HandGrab",
	"38_Handgrab.conf"	:	"9d800788f1b08800ae810202380a0822",
	"39_Handgrab.conf"	:	"5aca4d189052212118709018842178c0",
	"40_Handsqueezed.conf"	:	"HandSqueezed",
	"41_Handsqueezed.conf"	:	"208530c400c041818281048008011002",
	"42_Handwriting.conf"	:	"pencil",
	"43_Help.conf"	:	"question_arrow",
	"44_Help.conf"	:	"d9ce0ab605698f320427677b458ad60b",
	"45_Help.conf"	:	"5c6cd98b3f3ebcb1f9c7f1c204630408",
	"46_IBeam.conf"	:	"xterm",
	"47_IBeam.conf"	:	"ibeam",
	"48_Link.conf"	:	"link",
	"49_Link.conf"	:	"3085a0e285430894940527032f8b26df",
	"50_Link.conf"	:	"640fb0e74195791501fd1ed57b41487f",
	"51_Link.conf"	:	"0876e1c15ff2fc01f906f1c363074c0f",
	"52_NO.conf"	:	"crossed_circle",
	"53_NO.conf"	:	"dnd-none",
	"54_NO.conf"	:	"03b6e0fcb3499374a867c041f52298f0",
	"55_Move.conf"	:	"move",
	"56_Move.conf"	:	"plus",
	"57_Move.conf"	:	"4498f0e0c1937ffe01fd06f973665830",
	"58_Move.conf"	:	"9081237383d90e509aa00f00170e968f",
	"59_SizeAll.conf"	:	"fleur",
	"60_AngleNE.conf"	:	"bottom_left_corner",
	"61_AngleNE.conf"	:	"fd_double_arrow",
	"62_AngleNE.conf"	:	"top_right_corner",
	"63_AngleNE.conf"	:	"fcf1c3c7cd4491d801f1e1c78f100000",
	"64_BaseN.conf"	:	"bottom_side",
	"65_BaseN.conf"	:	"double_arrow",
	"66_BaseN.conf"	:	"top_side",
	"67_BaseN.conf"	:	"00008160000006810000408080010102",
	"68_AngleNW.conf"	:	"bd_double_arrow",
	"69_AngleNW.conf"	:	"bottom_right_corner",
	"70_AngleNW.conf"	:	"top_left_corner",
	"71_AngleNW.conf"	:	"c7088f0f3e6c8088236ef8e1e3e70000",
	"72_SizeWE.conf"	:	"left_side",
	"73_SizeWE.conf"	:	"right_side",
	"74_SizeWE.conf"	:	"028006030e0e7ebffc7f7070c0600140",
	"75_UpArrow.conf"	:	"center_ptr",
	"76_UpArrow.conf"	:	"sb_up_arrow",
	"77_DownArrow.conf"	:	"sb_down_arrow",
	"78_LeftArrow.conf"	:	"sb_left_arrow",
	"79_RightArrow.conf"	:	"sb_right_arrow",
	"80_HDoubleArrow.conf"	:	"h_double_arrow",
	"81_HDoubleArrow.conf"	:	"sb_h_double_arrow",
	"82_HDoubleArrow.conf"	:	"14fef782d02440884392942c11205230",
	"83_VDoubleArrow.conf"	:	"v_double_arrow",
	"84_VDoubleArrow.conf"	:	"sb_v_double_arrow",
	"85_VDoubleArrow.conf"	:	"2870a09082c103050810ffdffffe0204",
	"86_Wait.conf"	:	"watch",
	"87_X.conf"	:	"X_cursor",
	"88_X.conf"	:	"X-cursor",
	"89_ZoomIn.conf"	:	"zoomIn",
	"90_ZoomIn.conf"	:	"f41c0e382c94c0958e07017e42b00462",
	"91_ZoomOut.conf"	:	"zoomOut",
	"92_ZoomOut.conf"	:	"f41c0e382c97c0938e07017e42800402"
	}

	logging.debug("\n\t[Building Cursors]")
	xcursorgen_path = subprocess.check_output(["which", "xcursorgen"]).strip()
	src_folder = cursor_folder + "src/"
	build_folder = cursor_folder + "cursors/"
	shutil.rmtree(build_folder)
	os.mkdir(build_folder)
	for gen in xcursors_conf:
		conf_file = src_folder + gen[3:]
		cursor_file_output = build_folder + xcursors_conf[gen]
		logging.info("\t{:<21} {}".format(os.path.split(conf_file)[1], os.path.split(cursor_file_output)[1]))
		args = [
			xcursorgen_path,
			"-p",
			src_folder,
			conf_file,
			cursor_file_output
		]
		subprocess.check_call(args, stdout=subprocess.DEVNULL)

def parse_ani(file_name):
	# convert an ani file to a list of bytearray icons
	# input: ani file location/name

	f = open(file_name,'rb')
	ani_file = f.read()
	f.close()
	ani_bytes = bytearray(ani_file)

	loc = ani_bytes.find("anih".encode()) + 8
	anih = {
	"size"         : 0,
	"num_frames"   : 0,
	"num_steps"    : 0,
	"width"        : 0,
	"height"       : 0,
	"bit_count"    : 0,
	"num_planes"   : 0,
	"jif_rate"     : 0,
	"flags"        : 0
	}

	for i in anih: 
		anih[i] = int.from_bytes(ani_bytes[loc:loc+4],"little")
		loc +=4

	logging.debug("[ANI Header]")
	for i in anih:
		logging.debug("\t{:<30} {}".format(i,anih[i]))

	rate_length = anih["jif_rate"]
	if ani_bytes.find("rate".encode()) > -1:
		rate_length = []
		logging.debug("\n[Rate]")
		loc = ani_bytes.find("rate".encode()) + 4
		rate_size =  int.from_bytes(ani_bytes[loc:loc+4],"little")
		loc += 4
		for i in range(anih["num_steps"]):
			rate_length.append(int.from_bytes(ani_bytes[loc:loc+4],"little"))
			loc += 4
		logging.debug("\t{}".format(rate_length))

	seq_length = False
	if ani_bytes.find("seq ".encode()) > -1:
		seq_length = []
		logging.debug("\n[Seq]")
		loc = ani_bytes.find("seq ".encode()) + 4
		seq_size =  int.from_bytes(ani_bytes[loc:loc+4],"little")
		loc += 4
		for i in range(anih["num_steps"]):
			seq_length.append(int.from_bytes(ani_bytes[loc:loc+4],"little"))
			loc += 4
		logging.debug("\t{}".format(seq_length))

	# Now find the icons
	loc = ani_bytes.find("LIST".encode()) + 4
	num_icons = int.from_bytes(ani_bytes[loc:loc+4],"little")
	loc = ani_bytes.find("fram".encode()) + 8
	icons = []
	count = 0
	## At first icon
	for i in range(anih["num_steps"]):
		icon_size =  int.from_bytes(ani_bytes[loc:loc+4],"little")
		icon = ani_bytes[loc+4:(loc+4)+icon_size]
		icons.append(icon)	
		loc = loc + icon_size + 8
		count = count + 1

	return icons, seq_length, rate_length

def convert_icon(folder, ico_file_name, theme_folder, squaresize = 20, overlap = 2, tmp_file="./chicago95_tmp_file.svg", max_colors=25 ):
	## Converts Icons to PNG
	# Input:
	#  folder: svg file destination folder
	#  ico_file_name: theme icon file to be processed
	#  theme_folder: dict of the folder for case insensitivty
	#  squaresize: how big svg 'pixels'
	#  overlap: do the squares overlap
	#  tmp_file: tmp working file for inkscape
	#  max_colors = max colors to try and merge in svg
	# Lots of code lifted from pixel2svg


	path_to_icon, icon_file_name = os.path.split(ico_file_name)
	icon_name, icon_ext = os.path.splitext(icon_file_name)
	svg_name = icon_name+".svg"

	if not os.path.exists(ico_file_name):
		for lower_file in theme_folder:
			if ico_file_name in lower_file:
				ico_file_name = theme_folder[lower_file]
		
	# Open the icon file
	image = Image.open(ico_file_name)
	image = image.convert("RGBA")
	(width, height) = image.size
	rgb_values = list(image.getdata())
	rgb_values = list(image.getdata())
	svgdoc = svgwrite.Drawing(filename = folder + svg_name,
	                          size = ("{0}px".format(width * squaresize),
	                          "{0}px".format(height * squaresize)))
	# If --overlap is given, use a slight overlap to prevent inaccurate SVG rendering
	rectangle_size = ("{0}px".format(squaresize + overlap),
	                  "{0}px".format(squaresize + overlap))
	rowcount = 0
	while rowcount < height:
		colcount = 0
		while colcount < width:
			rgb_tuple = rgb_values.pop(0)
			# Omit transparent pixels
			if rgb_tuple[3] > 0:
				rectangle_posn = ("{0}px".format(colcount * squaresize),
					  "{0}px".format(rowcount * squaresize))
				rectangle_fill = svgwrite.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
				alpha = rgb_tuple[3];
				if alpha == 255:
					svgdoc.add(svgdoc.rect(insert = rectangle_posn,
				                   size = rectangle_size,
				                   fill = rectangle_fill))
				else:
					svgdoc.add(svgdoc.rect(insert = rectangle_posn,
		          	        	 size = rectangle_size,
		          	        	 fill = rectangle_fill,
		          		         opacity = alpha/float(255)))
			colcount = colcount + 1
		rowcount = rowcount + 1
	svgdoc.save()
	convert_to_proper_svg_with_inkscape(tmp_file, svgdoc.filename)
	SVG_NS = "http://www.w3.org/2000/svg"
	svg = ET.parse(tmp_file)
	rects = svg.findall('.//{%s}rect' % SVG_NS)
	rgbs = {}
	for rect in rects:
		rect_id = rect.attrib['id']
		rgb = rect.attrib['fill']
		if rgb not in rgbs:
			rgbs[rgb] = rect_id

	if len(rgbs) < max_colors:
		print("\tinkscape will open {} times to process {}. (use option -v for more information)".format(len(rgbs), svg_name))
	else:
		logging.info("{:<21} too many colors ({}>{}), skipping".format(svg_name, len(rgbs), max_colors))
	
	count = 0
	for rgb in rgbs:
		count = count + 1
		if len(rgbs) >= max_colors:
			break
		#if count % 10 == 0:
		logging.info("{:<21} [{:<3} / {:<3} {:<5}] Converting {}".format(' ',count, len(rgbs),str(round((float(count)/float(len(rgbs))*100),0)), rgb ))
		fix_with_inkscape( rgbs[rgb] , tmp_file )

	shutil.move(tmp_file, svgdoc.filename)
	return(svgdoc.filename)

def fix_with_inkscape(color, tmpfile):
	inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()
	args = [
	inkscape_path,
	"--select="+color,
	"--verb", "EditSelectSameFillColor",
	"--verb", "SelectionCombine", 
	"--verb", "SelectionUnion", 
	"--verb", "FileSave", 
	"--verb", "FileQuit",
	tmpfile
	]
	subprocess.check_call(args, stderr=subprocess.DEVNULL ,stdout=subprocess.DEVNULL)

def convert_to_png_with_inkscape(svg_in, size, png_out):
	inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()	
	size = str(size)
	args = [
	inkscape_path,
	"--without-gui",
	"-f", svg_in,
	"--export-area-page",
	"-w", size,
	"-h", size,
	"--export-png=" + png_out
	]
	subprocess.check_call(args, stdout=subprocess.DEVNULL)

def convert_to_proper_svg_with_inkscape(svg_out, svg_in):
	inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()
	args = [
	inkscape_path,
	"-l", svg_out, svg_in
	]
	subprocess.check_call(args, stdout=subprocess.DEVNULL)

def xfconf_query(svg_out, svg_in):
	inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()
	args = [
	inkscape_path,
	"-l", svg_out, svg_in
	]
	subprocess.check_call(args, stdout=subprocess.DEVNULL)

def get_file_name(config, section, key):
	#input:
	#  config  = parsed .theme file
	#  section = the section in the config file
	#  key     = key in theme file
	# Returns: filename
	# To Do: incorporate icon number
	reg_key = "Software\\Classes\\"
	file_name = ''
	icon_number = 0
	if section in config and key in config[section]:
		file_name = config[section][key].lower()
	elif reg_key+section in config and key in config[reg_key+section]:
		file_name = config[reg_key+section][key].lower()
	else:
		return False

	if file_name == '':
		# The key was here but its empty
		return False

	if "%windir%" in file_name:
		# we dont bother changing system icons
		return False
	
	if "%ThemeDir%".lower() in file_name:
		file_name = file_name.replace("%ThemeDir%".lower(),'')
	
	if "," in file_name: 
		file_name, icon_number = file_name.split(",")
	file_name = file_name.split("\\")[-1]

	return file_name

def null_string(data):
	data = bytearray(data)
	return data[:data.find(0)].decode('ascii')


def parse_IconMetrics(IconMetrics):
	font_weight = {
		"0":"FW_DONTCARE",
		"100":"FW_THIN",
		"200":"FW_EXTRALIGHT",
		"200":"FW_ULTRALIGHT",
		"300":"FW_LIGHT",
		"400":"FW_NORMAL",
		"400":"FW_REGULAR",
		"500":"FW_MEDIUM",
		"600":"FW_SEMIBOLD",
		"600":"FW_DEMIBOLD",
		"700":"FW_BOLD",
		"800":"FW_EXTRABOLD",
		"800":"FW_ULTRABOLD",
		"900":"FW_HEAVY",
		"900":"FW_BLACK"
	}

	x = []
	for i in IconMetrics.split():
		x.append(int(i))

 
	iconmetrics = {
	"cbSize" 	: int.from_bytes(x[0:4],"little"),
	"iHorzSpacing"	: int.from_bytes(x[4:8],"little"),
	"iVertSpacing"	: int.from_bytes(x[8:12],"little"),
	"iTitleWrap"	: int.from_bytes(x[12:16],"little")
	}

	lfFont = {
	"Name:" : "lfFont",
	"lfHeight" : int.from_bytes(x[16:20],"little"),
	"lfWidth" : int.from_bytes(x[20:24],"little"),
	"lfEscapement" : int.from_bytes(x[24:28],"little"),
	"lfOrientation" : int.from_bytes(x[28:32],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[32:36],"little"))],
	"lfItalic" : x[37],
	"lfUnderline" : x[38],
	"lfStrikeOut" : x[39],
	"lfCharSet" :  x[40],
	"lfOutPrecision" : x[41],
	"lfClipPrecision" : x[42],
	"lfQuality" : x[43],
	"lfPitchAndFamily" : x[44],
	 "lfFaceName[32]" : null_string(x[44:44+32])
	}
	logging.info("[iconmetrics]")
	for i in iconmetrics:
		logging.info("\t{:<21} {}".format(i, iconmetrics[i]))
	logging.info("[lfFont]")
	for i in lfFont:
		logging.info("\t{:<21} {}".format(i, lfFont[i]))


def parse_NONCLIENTMETRICS(NONCLIENTMETRICSA):
	font_weight = {
		"0":"FW_DONTCARE",
		"100":"FW_THIN",
		"200":"FW_EXTRALIGHT",
		"200":"FW_ULTRALIGHT",
		"300":"FW_LIGHT",
		"400":"FW_NORMAL",
		"400":"FW_REGULAR",
		"500":"FW_MEDIUM",
		"600":"FW_SEMIBOLD",
		"600":"FW_DEMIBOLD",
		"700":"FW_BOLD",
		"800":"FW_EXTRABOLD",
		"800":"FW_ULTRABOLD",
		"900":"FW_HEAVY",
		"900":"FW_BLACK"
	}

	x = []
	for i in NONCLIENTMETRICSA.split():
		x.append(int(i))


	nonclientmetrics = {
	"cbSize" 	: int.from_bytes(x[0:4],"little"),
	"iBorderWidth"	: int.from_bytes(x[4:8],"little"),
	"iScrollWidth"	: int.from_bytes(x[8:12],"little"),
	"iScrollHeight"	: int.from_bytes(x[12:16],"little"),
	"iCaptionWidth"	: int.from_bytes(x[16:20],"little"),
	"iCaptionHeight": int.from_bytes(x[20:24],"little")
	}

	lfcaptionfont = {
	"Name:" : "lfcaptionfont",
	"lfHeight" : int.from_bytes(x[24:28],"little"),
	"lfWidth" : int.from_bytes(x[28:32],"little"),
	"lfEscapement" : int.from_bytes(x[32:36],"little"),
	"lfOrientation" : int.from_bytes(x[36:40],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[40:44],"little"))],
	"lfItalic" : x[44],
	"lfUnderline" : x[45],
	"lfStrikeOut" : x[46],
	"lfCharSet" :  x[47],
	"lfOutPrecision" : x[48],
	"lfClipPrecision" : x[49],
	"lfQuality" : x[50],
	"lfPitchAndFamily" : x[51],
	 "lfFaceName[32]" : null_string(x[52:52+32])
	}

	nonclientmetrics["iSmCaptionWidth"] = int.from_bytes(x[84:88],"little")
	nonclientmetrics["iSmCaptionHeight"] = int.from_bytes(x[88:92],"little")

	lfSmCaptionFont = {
	"Name" : "lfSmCaptionFont",
	"lfHeight" : int.from_bytes(x[92:96],"little"),
	"lfWidth" : int.from_bytes(x[96:100],"little"),
	"lfEscapement" : int.from_bytes(x[100:104],"little"),
	"lfOrientation" : int.from_bytes(x[104:108],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[108:112],"little"))],
	"lfItalic" : x[112],
	"lfUnderline" : x[113],
	"lfStrikeOut" : x[114],
	"lfCharSet" :  x[115],
	"lfOutPrecision" : x[116],
	"lfClipPrecision" : x[117],
	"lfQuality" : x[118],
	"lfPitchAndFamily" : x[119],
	 "lfFaceName[32]" : null_string(x[120:120+32])
	}

	nonclientmetrics["iMenuWidth"] = int.from_bytes(x[152:156],"little")
	nonclientmetrics["iMenuHeight"] = int.from_bytes(x[156:160],"little")

	lfMenuFont = {
	"Name" : "lfMenuFont",
	"lfHeight" : int.from_bytes(x[160:164],"little"),
	"lfWidth" : int.from_bytes(x[164:168],"little"),
	"lfEscapement" : int.from_bytes(x[168:172],"little"),
	"lfOrientation" : int.from_bytes(x[172:176],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[176:180],"little"))],
	"lfItalic" : x[180],
	"lfUnderline" : x[181],
	"lfStrikeOut" : x[182],
	"lfCharSet" :  x[183],
	"lfOutPrecision" : x[184],
	"lfClipPrecision" : x[185],
	"lfQuality" : x[186],
	"lfPitchAndFamily" : x[187],
	 "lfFaceName[32]" : null_string(x[188:188+32])
	}

	lfStatusFont = {
	"Name" : "lfStatusFont",
	"lfHeight" : int.from_bytes(x[220:224],"little"),
	"lfWidth" : int.from_bytes(x[224:228],"little"),
	"lfEscapement" : int.from_bytes(x[228:232],"little"),
	"lfOrientation" : int.from_bytes(x[232:236],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[236:240],"little"))],
	"lfItalic" : x[240],
	"lfUnderline" : x[241],
	"lfStrikeOut" : x[242],
	"lfCharSet" :  x[243],
	"lfOutPrecision" : x[244],
	"lfClipPrecision" : x[245],
	"lfQuality" : x[246],
	"lfPitchAndFamily" : x[247],
	 "lfFaceName[32]" : null_string(x[248:248+32])
	}

	lfMessageFont = {
	"Name" : "lfMessageFont",
	"lfHeight" : int.from_bytes(x[280:284],"little"),
	"lfWidth" : int.from_bytes(x[284:288],"little"),
	"lfEscapement" : int.from_bytes(x[288:292],"little"),
	"lfOrientation" : int.from_bytes(x[292:296],"little"),
	"lfWeight" : font_weight[str(int.from_bytes(x[296:300],"little"))],
	"lfItalic" : x[300],
	"lfUnderline" : x[301],
	"lfStrikeOut" : x[302],
	"lfCharSet" :  x[303],
	"lfOutPrecision" : x[304],
	"lfClipPrecision" : x[305],
	"lfQuality" : x[306],
	"lfPitchAndFamily" : x[307],
	 "lfFaceName[32]" : null_string(x[308:308+32])
	}
	logging.info("[nonclientmetrics]")
	for i in nonclientmetrics:
		logging.info("\t{:<21} {}".format(i, nonclientmetrics[i]))
	logging.info("[lfcaptionfont]")
	for i in lfcaptionfont:
		logging.info("\t{:<21} {}".format(i, lfcaptionfont[i]))
	logging.info("[lfSmCaptionFont]")
	for i in lfSmCaptionFont:
			logging.info("\t{:<21} {}".format(i, lfSmCaptionFont[i]))
	logging.info("[lfMenuFont]")
	for i in lfMenuFont:
			logging.info("\t{:<21} {}".format(i, lfMenuFont[i]))
	logging.info("[lfStatusFont]")	
	for i in lfStatusFont:
			logging.info("\t{:<21} {}".format(i, lfStatusFont[i]))
	logging.info("[lfMessageFont]")
	for i in lfMessageFont:
			logging.info("\t{:<21} {}".format(i, lfMessageFont[i]))

	return lfcaptionfont["lfFaceName[32]"], lfcaptionfont["lfWeight"]


def main():
	print(plus)
	print("Microsoft Theme file parser")
	desc = '''Chicago95 Plus! is a python script that can parse Windows 95/98/ME/XP theme files and create new Chicago95 themes. Chicago95 Plus! supports Icons, Cursors, Fonts, Wallpapers and Theme colors! Use this against themes you can find on ThemeWorld or any site that have Windows Plus! Themes!\nThis script can be called from any folder, execute it and provide it the path to a theme file (e.g. %(prog)s /home/bgates/Wicked/Wicked.theme) and your new theme will be created!'''
	arg_parser = argparse.ArgumentParser(description=desc, 
						usage='%(prog)s [options] MS_Theme_File', 
						epilog="Part of the Chicago95 theme project",
						formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	arg_parser.add_argument('-d', '--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
	arg_parser.add_argument("--noinstall", help="Do not place folders nor change theme", action="store_true")
	arg_parser.add_argument("--info", help="Does nothing except give information about the theme file", action="store_true")
	arg_parser.add_argument('-c', '--colors', help='How many colors before skipping Inkscape fix/merge for SVGs. Set to 1 to speed up conversion. WARNING: This may result in transparent icons!', default=32, type=int)
	arg_parser.add_argument('-o', '--overlap', help='Pixel overlap for SVG icons', default=1, type=int)	
	arg_parser.add_argument('-s', '--squaresize', help='Square size for SVG icons', default=20, type=int)	
	arg_parser.add_argument("--installdir", help="Folder to create new theme in, default is current working directory", default=os.getcwd())
	arg_parser.add_argument("theme_file", help="Microsoft Windows 95/98/ME .theme file")
	args = arg_parser.parse_args()	

	if args.info:
		args.loglevel = logging.INFO

	logging.basicConfig(level=args.loglevel, format="\t%(message)s")

	error = False

	if not os.path.exists(str(Path.home())+"/.icons/Chicago95") and not os.path.exists(str(Path.home())+"/.icons/Chicago95_tux"):
		print("\nERROR: Either the Chicago95 or Chicago95_tux icon theme must be installed to {} to use this script\n".format(str(Path.home())+"/.icons/"))
		error = True

	if not os.path.exists(str(Path.home())+"/.icons/Chicago95_Cursor_Black"):
		print("\nERROR: The Chicago95 cursor Chicago95_Cursor_Black must be installed to {} to use this script\n".format(str(Path.home())+"/.icons/"))
		error = True

	if not os.path.exists(str(Path.home())+"/.themes/Chicago95"):
		print("\nERROR: The Chicago95 theme must be installed to {} to use this script\n".format(str(Path.home())+"/.themes/"))
		error = True

	try:
		inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()
	except subprocess.CalledProcessError:
		print("\nERROR: You need inkscape installed to use this script.\n")
		error = True

	try:
		convert_path = subprocess.check_output(["which", "convert"]).strip()
	except subprocess.CalledProcessError:
		print("\nERROR: You need imagemagick installed to use this script.\n")
		error = True
	try:
		convert_path = subprocess.check_output(["which", "xcursorgen"]).strip()
	except subprocess.CalledProcessError:
		print("\nERROR: You need xcursorgen installed to use this script.\n")
		error = True

	if error:
		sys.exit(1)

	# Get the file name and extions in to useable names
	theme_file = args.theme_file
	path_to_theme, theme_file_name = os.path.split(theme_file)
	if len(path_to_theme) != 0:
		path_to_theme = path_to_theme + "/"
	else:
		path_to_theme = "./"
	theme_name_spaces, theme_ext = os.path.splitext(theme_file_name)
	index_theme_name = theme_name_spaces + "(Chicago 95 Variant)" # For various Index.theme files
	theme_name = theme_name_spaces.capitalize().replace(" ", "_")
	if args.installdir[-1] != "/": 
		new_theme_folder = args.installdir + "/" + theme_name + "_Chicago95/"
	else:
		new_theme_folder = args.installdir + theme_name + "_Chicago95/"

	print("[Parser] Parsing Theme File:", theme_file)
	#config = ConfigParser(dict_type=CaseInsensitiveDict,interpolation=None)
	config = ConfigParser(interpolation=None)
	config.read(theme_file)

	# Themes have a weird structure we use thise dict to remove case but keep the filename
	theme_files = {}

	for root, dirs, files in os.walk(path_to_theme, topdown=False):
		for name in files:
			theme_files[os.path.join(root, name).lower()] = os.path.join(root, name)

	## Get the icons
	print("[Parser] Parsing Icons")
	icons = {}

	icons["my_computer"]  = get_file_name(config,"CLSID\\{20D04FE0-3AEA-1069-A2D8-08002B30309D}\\DefaultIcon","DefaultValue")

	if get_file_name(config,"CLSID\\{450D8FBA-AD25-11D0-98A8-0800361B1103}\\DefaultIcon","DefaultValue"):
		icons["my_documents"] = get_file_name(config,"CLSID\\{450D8FBA-AD25-11D0-98A8-0800361B1103}\\DefaultIcon","DefaultValue")
	elif get_file_name(config,"CLSID\\{59031A47-3F72-44A7-89C5-5595FE6B30EE}\\DefaultIcon","DefaultValue"):
		icons["my_documents"] = get_file_name(config,"CLSID\\{59031A47-3F72-44A7-89C5-5595FE6B30EE}\\DefaultIcon","DefaultValue")
	else:
		icons["my_documents"] = False

	if get_file_name(config,"CLSID\\{208D2C60-3AEA-1069-A2D7-08002B30309D}\\DefaultIcon","DefaultValue"):
		icons["network_neighborhood"] = get_file_name(config,"CLSID\\{208D2C60-3AEA-1069-A2D7-08002B30309D}\\DefaultIcon","DefaultValue")
	elif get_file_name(config,"CLSID\\{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}\\DefaultIcon","DefaultValue"):
		icons["network_neighborhood"] =  get_file_name(config,"CLSID\\{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}\\DefaultIcon","DefaultValue")
	else:
		icons["network_neighborhood"] = False

	icons["recycle_bin_full"]  = get_file_name(config,"CLSID\\{645FF040-5081-101B-9F08-00AA002F954E}\\DefaultIcon","Full")

	icons["recycle_bin_empty"] = get_file_name(config,"CLSID\\{645FF040-5081-101B-9F08-00AA002F954E}\\DefaultIcon","Empty")

	for i in icons:
		logging.info("{:<21} {}".format(i,icons[i]))

	print("[Parser] Parsing Colors")
	colors = {}
	if "Control Panel\Colors" in config:
		for color_name in config["Control Panel\Colors"]:
			r, g, b = config["Control Panel\Colors"][color_name].split()
			colors[color_name] = '#{:02x}{:02x}{:02x}'.format(int(r),int(g),int(b))
			logging.info("{:<21} {:<7} ({:<15})".format(color_name, colors[color_name], config["Control Panel\Colors"][color_name]))

	print("[Parser] Parsing Cursors")
	cursors = {}
	if "Control Panel\Cursors" in config:
		for cursor_name in config["Control Panel\Cursors"]:		
			cursors[cursor_name] =  get_file_name(config,"Control Panel\Cursors",cursor_name)
			logging.info("{:<21} {}".format(cursor_name, cursors[cursor_name]))


	## Get Sound files
	print("[Parser] Parsing Sounds")
	sound_names = [
	"AppEvents\\Schemes\\Apps\\.Default\\AppGPFault\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\Close\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\.Default\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\MailBeep\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\Maximize\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\MenuCommand\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\MenuPopup\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\Minimize\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\Open\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\RestoreDown\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\RestoreUp\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\RingIn\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\Ringout\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemAsterisk\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemDefault\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemExclamation\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemExit\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemHand\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemQuestion\\.Current",
	"AppEvents\\Schemes\\Apps\\.Default\\SystemStart\\.Current",
	"AppEvents\\Schemes\\Apps\\Explorer\\EmptyRecycleBin\\.Current"
	]

	sounds = {}
	for i in sound_names:
		sound_name = i.split("\\")[-2]
		if get_file_name(config,i,"DefaultValue"):
			wav_file = get_file_name(config,i,"DefaultValue")
			sounds[sound_name] = wav_file
			logging.info("{:<21} {}".format(sound_name, wav_file))

	#Screen Saver
	screensaver = False
	if "boot" in config:
		print("[Parser] Parsing Boot (screensaver)")
		screensaver = get_file_name(config,"boot","SCRNSAVE.EXE")
		logging.info("{:<21} {}".format("screensaver",screensaver))
	## Get the wallpaper
	wallpaper = False
	if "Control Panel\Desktop" in config:
		print("[Parser] Parsing Wallpaper")
		wallpaper = get_file_name(config,"Control Panel\Desktop","Wallpaper")
		logging.info("{:<21} {}".format("wallpaper",wallpaper))
	#NonClientMetrics/IconMetrics
	print("[Parser] Parsing NonClientMetrics")
	NonclientMetrics = config["Metrics"]["nonclientmetrics"]
	(lfcaptionfont, weight) = parse_NONCLIENTMETRICS(NonclientMetrics)
	print("[Parser] Parsing IconMetrics")
	IconMetrics = config["Metrics"]["iconmetrics"]
	parse_IconMetrics(IconMetrics)

	print("[Parser] Parsing Complete!\n\n", "=" * 80)
	if args.info:
		print("\nThank you for using Chicago95 Plus!\n")
		sys.exit()
	print("\n[Theme Builder]\tMaking folders for theme: {}".format(theme_name))

	chicago95_icons_folder   = str(Path.home())+"/.icons/Chicago95" if os.path.exists(str(Path.home())+"/.icons/Chicago95") else str(Path.home())+"/.icons/Chicago95_tux"
	chicago95_cursors_folder = str(Path.home())+"/.icons/Chicago95_Cursor_Black"
	chicago95_theme_folder   = str(Path.home())+"/.themes/Chicago95"

	folder_names = {
		"root"    : new_theme_folder,
		"icons"   : new_theme_folder + theme_name + "_Icons/",
		"theme"   : new_theme_folder + theme_name + "_Theme/",
		"cursors" : new_theme_folder + theme_name + "_Cursors/",
		"sounds"  : new_theme_folder + theme_name + "_Sounds/"
		 }

	for i in folder_names:
		logging.info("{:<21} {}".format(i,folder_names[i]))
		shutil.rmtree(folder_names[i], ignore_errors=True)
		if i == "icons":
			shutil.copytree(chicago95_icons_folder,folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
		elif i == "cursors":
			shutil.copytree(chicago95_cursors_folder,folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
		#elif i == "theme":
		#	shutil.copytree(chicago95_theme_folder,folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
		else:
			os.mkdir(folder_names[i])
		
	print("[Icons]\t\tCreating new icons in {}".format(folder_names['icons']))
	icon_sizes = [16,22,24,32,48]
	svg_file_names = {}
	png_file_names = {
		 "my_computer"           : "user-home.png",
		 "my_documents"          : "folder-documents.png",
		 "network_neighborhood"  : "network-server.png",
		 "recycle_bin_empty"     : "user-trash.png",
		 "recycle_bin_full"      : "user-trash-full.png"
		 }
	for i in png_file_names:
		svg_file_names[i] = png_file_names[i].replace(".png",".svg")

	for i in icons:
		if not icons[i]: #Skip ithe icon if it doesn't exist in the theme
			continue
		svg_icon_file = convert_icon(folder_names['icons'],icons[i], theme_files, squaresize = args.squaresize, overlap = args.overlap, max_colors=args.colors)
		for size in icon_sizes:
			if size <= 32 and i == "documents_ico": 
				continue
			sized_target = folder_names['icons']+"places/"+str(size)+"/"+png_file_names[i]
			logging.info("Size: {:<21} {} {}".format(size, svg_icon_file, sized_target))
			convert_to_png_with_inkscape( svg_icon_file, size, sized_target)

		scaled_target = folder_names['icons']+"places/scalable/"+svg_file_names[i]
		shutil.copy(svg_icon_file, scaled_target)

	# Now replace Icons
	icon_theme_config = configparser.RawConfigParser(interpolation=None)
	icon_theme_config.optionxform = str
	icon_theme_config.read(folder_names['icons']+"/index.theme")
	icon_theme_config.set("Icon Theme","Name",index_theme_name)
	with open(folder_names['icons']+"/index.theme", 'w') as configfile:
	    icon_theme_config.write(configfile,  space_around_delimiters=False)


	# Cursors
	print("[Cursors]\tGenerating New cursors in {}".format(folder_names['cursors']))


	pointers = {
		"arrow"       : "Arrow",
		"help"        : "Help",
		"appstarting" : "AppStarting",
		"wait"        : "Wait",
		"nwpen"       : "Handwriting",
		"no"          : "NO",
		"sizens"      : "BaseN",
		"sizewe"      : "SizeWE",
		"crosshair"   : "Crosshair",
		"ibeam"       : "IBeam",
		"sizenwse"    : "AngleNE",
		"sizenesw"    : "AngleNW",
		"sizeall"     : "SizeAll",
		"uparrow"     : "UpArrow"
		}

	cursor_src_folder = folder_names['cursors'] + "src/"

	for current_cursor in pointers:
		if current_cursor not in cursors or not cursors[current_cursor]: 
			continue
		if not os.path.exists(path_to_theme+cursors[current_cursor]):
			for lower_file in theme_files:
				if cursors[current_cursor] in lower_file:
					theme_cursor_file_name = theme_files[lower_file]
		else:
			theme_cursor_file_name = cursors[current_cursor]

		x11_cursor_file_name = cursor_src_folder+pointers[current_cursor]+".png"
		os.remove(x11_cursor_file_name)
		logging.info("{:<21} {}".format(os.path.split(theme_cursor_file_name)[1],os.path.split(x11_cursor_file_name)[1]))
		if os.path.splitext(cursors[current_cursor])[1] in ".ani":
			icon_cur_files, seq, rate = parse_ani(theme_cursor_file_name)
			icon_file_names = make_x11_cursors(icon_cur_files, seq, rate, theme_cursor_file_name, cursor_src_folder)
			with open(cursor_src_folder+pointers[current_cursor]+".conf") as f:
				(g1, g2, g3, cursor_n) = f.readline().strip().split(" ")
			write_conf = open(cursor_src_folder+pointers[current_cursor]+".conf", 'w')
			logging.debug("\n[Convert]")
			for icon_cur in icon_file_names:
				x11_cursor_file_name = cursor_src_folder+pointers[current_cursor]+".png"
				path_to_src, png_file_name = os.path.split(x11_cursor_file_name)
				cur_name = os.path.splitext(png_file_name)[0]
				path_to_icon, icon_file_name = os.path.split(icon_cur)
				orig_icon_name = os.path.splitext(icon_file_name)[0]
				seq = orig_icon_name.split("_")[-1]
				rate = orig_icon_name.split("_")[-2]
				x11_cursor_file_name =  x11_cursor_file_name[:-4] + "_{}_{}.png".format(rate, seq)
				convert_icon_files(icon_cur,x11_cursor_file_name)
				# Xcursorgen conf file format: <size> <xhot> <yhot> <filename> <ms-delay>
				# Ani to png file format: <filename> <jiffie> <sequence>
				cursor_conf_string = "{} {} {} {} {}\n".format(g1, g2, g3, os.path.split(x11_cursor_file_name)[1],int(rate) * 17 )
				write_conf.write(cursor_conf_string)
				
			write_conf.close()
		else:
			convert_icon_files(theme_cursor_file_name,x11_cursor_file_name)
	
	# Cursors are all done now we need to generate X11 cursors with xcursorgen
	build_cursors(folder_names['cursors'])
	cur_theme_config = configparser.RawConfigParser(interpolation=None)
	cur_theme_config.optionxform = str
	cur_theme_config.read(folder_names['cursors']+"index.theme")
	cur_theme_config.set("Icon Theme","Name",index_theme_name)
	with open(folder_names['cursors']+"index.theme", 'w') as configfile:
	    cur_theme_config.write(configfile,  space_around_delimiters=False)
		


	print("[Colors]\tChanging theme colors in {}".format(folder_names['theme']))

	original_theme_folder = os.path.expanduser("~/.themes/Chicago95")
	target_theme_folder = folder_names["theme"]
	remapColors = {
		"#000080": colors['activetitle'],	#Active Window and Text Highlight - RED
		"#dfdfdf": colors['menu'],	#highlight? - Does Nothing - Yellow
		"#c0c0c0": colors['menu'],	#main window outline/buttons/bars color and inactive text - Green
		"#ffffff": colors['window'],	#main window color inner and main text color - Blue
		"#808080": colors['inactivetitle'],	#shadow window color (Inactive?) - turqoise
		"#000000": colors['windowtext'],	#Inactive window text color	- Purple
	}

	#Make sure none of them overlap
	for x in remapColors:
		if remapColors[x] in remapColors:
			if x.lower() == remapColors[x].lower():
				continue
			elif remapColors[x][-1].lower() == 'f':
				remapColors[x] = remapColors[x][:6] + 'e'
			else:
				remapColors[x] = remapColors[x][:6] + str(int(remapColors[x][-1]) + 1)
	for i in remapColors:
		logging.info("\tCurrent: {:<12} New Color: {}".format(i,remapColors[i]))

	if (os.path.isdir(target_theme_folder)):
		shutil.rmtree(target_theme_folder)

	os.makedirs(target_theme_folder)

	for root,dirs,files in os.walk(original_theme_folder):
		for dir in dirs:
			fpath = os.path.join(root,dir)
			nfpath = fpath.replace(original_theme_folder,target_theme_folder)
			if not (os.path.isdir(nfpath)):
				os.makedirs(nfpath)
		
		for file in files:
			fpath = os.path.join(root,file)
			nfpath = fpath.replace(original_theme_folder,target_theme_folder)
			lpath = fpath.replace(original_theme_folder + "/","")
			ext = os.path.splitext(fpath)[1].lower()

			if (ext == ".css") or (ext == ".scss") or (ext == ".xpm") or (ext == ".svg") or (ext == ".rc")\
			or (lpath == "gtk-2.0/gtkrc") or (lpath == "xfwm4/hidpi/themerc") or (lpath == "xfwm4/themerc"):
				fileh = open(fpath,"r")
				nfileh = open(nfpath,"w")
				for line in fileh:
					for color in remapColors:
						if color.lower() == remapColors[color].lower():
							continue
						if color.upper() in line:
							logging.debug("\t{:<30} from: {} to: {}".format( os.path.split(fpath)[1],color,remapColors[color]))
							line = line.replace(color.upper(),remapColors[color].upper())
						elif color.lower() in line:
							logging.debug("\t{:<30} from: {} to: {}".format( os.path.split(fpath)[1],color,remapColors[color]))
							line = line.replace(color.lower(),remapColors[color].lower())
					nfileh.write(line)
				fileh.close()
				nfileh.close()
			
			if (ext == ".png"):
				img = Image.open(fpath)
				img = img.convert("RGBA")
				pixels = img.load()
				width, height = img.size
				for y in range(height):
					for x in range(width):
						pixel = pixels[x,y]
						for color in remapColors:
							if color.lower() == remapColors[color].lower():
								continue
							colorV = remapColors[color]
							rgbColor = hexToRGB(color)
							rgbColorV = hexToRGB(colorV)
							if (rgbaToRGB(pixel) == rgbColor):
								logging.debug("\t{:<30} from: {} to: {}".format( os.path.split(fpath)[1],color,remapColors[color]))
								pixels[x,y] = (rgbColorV[0],rgbColorV[1],rgbColorV[2],pixel[3])
								break
		
				img.save(nfpath)
				img.close()
			
			if not (os.path.isfile(nfpath)):
				shutil.copy(fpath,nfpath)
	cur_theme_config = configparser.RawConfigParser(interpolation=None)
	cur_theme_config.optionxform = str
	cur_theme_config.read(folder_names['theme']+"index.theme")
	cur_theme_config.set("Desktop Entry","Name",index_theme_name)
	cur_theme_config.set("X-GNOME-Metatheme","GtkTheme",index_theme_name)
	cur_theme_config.set("X-GNOME-Metatheme","MetacityTheme",index_theme_name)
	cur_theme_config.set("X-GNOME-Metatheme","IconTheme",index_theme_name)
	cur_theme_config.set("X-GNOME-Metatheme","CursorTheme",index_theme_name)
	with open(folder_names['theme']+"index.theme", 'w') as configfile:
	    cur_theme_config.write(configfile,  space_around_delimiters=False)


	if wallpaper: 
		print("[Desktop]\tWallpaper: {}".format(wallpaper))
		theme_wallpaper = False
		if not os.path.exists(path_to_theme+wallpaper):
			for lower_file in theme_files:
				if wallpaper.lower() in lower_file:
					theme_wallpaper = theme_files[lower_file]
		else:
			theme_wallpaper = wallpaper
		if theme_wallpaper:	
			logging.info("{}".format(os.path.split(wallpaper)[1]))
			shutil.copy(theme_wallpaper,folder_names['root'])
			theme_wallpaper = folder_names['root'] + os.path.split(theme_wallpaper)[1]
		else:
			logging.info("Could not copy wallpaper {} to {}".format(path_to_theme+wallpaper,theme_screensaver))

	if screensaver: 
		print("[Screensaver]\t{0} copied to {1} (usage: wine {0} /s)".format(path_to_theme+screensaver, folder_names['root']))
		theme_screensaver = False
		if not os.path.exists(path_to_theme+screensaver):
			for lower_file in theme_files:
				if screensaver.lower() in lower_file:
					theme_screensaver = theme_files[lower_file]
		else:
			theme_screensaver = screensaver
		if theme_screensaver:	
			logging.info("{}".format(os.path.split(theme_screensaver)[1]))
			shutil.copy(theme_screensaver,folder_names['root'])
			theme_screensaver = folder_names['root'] + os.path.split(theme_screensaver)[1]
		else:
			logging.info("Could not copy screensaver {} to {}".format(path_to_theme+screensaver,theme_screensaver))

	print("[Fonts]\t\tGetting any font files")
	fonts = []
	for files in theme_files:
		if ".ttf" in files:
			logging.info("{}".format(os.path.split(files)[1]))
			shutil.copy(theme_files[files],folder_names['root']+os.path.split(files)[1])
			fonts.append(folder_names['root']+os.path.split(files)[1])

	print("[Colors]\tCopying Sounds to {}".format(folder_names['sounds']))
	for sound in sounds:
		if not sound:
			continue
		if not os.path.exists(path_to_theme+sounds[sound]):
			for lower_file in theme_files:
				if sounds[sound] in lower_file:
					theme_sound_file_name = theme_files[lower_file]
		else:
			theme_sound_file_name = sounds[sound]
		new_sound_file_name = "{}_{}".format(sound,sounds[sound].replace(" ","_"))
		logging.info("Sound: {} copying {} to {}".format(sound,theme_sound_file_name,folder_names['sounds']+new_sound_file_name))
		shutil.copy(theme_sound_file_name,folder_names['sounds']+new_sound_file_name)

	print("[Theme Builder]\tCompleted!\n")

	print("-" * 80)

	install_icons_dir   = str(Path.home())+"/.icons/"+folder_names['icons'].split("/")[-2]
	install_cursors_dir = str(Path.home())+"/.icons/"+folder_names['cursors'].split("/")[-2]
	install_themes_dir  = str(Path.home())+"/.themes/"+folder_names['theme'].split("/")[-2]

	if not args.noinstall:

		print("\n[Installing]")	
		shutil.rmtree(install_icons_dir, ignore_errors=True)
		shutil.rmtree(install_cursors_dir, ignore_errors=True)
		shutil.rmtree(install_themes_dir, ignore_errors=True)

		logging.info("\tCopying {} to {}".format(folder_names['icons'], install_icons_dir))
		shutil.copytree(folder_names['icons'],install_icons_dir,symlinks=True,ignore_dangling_symlinks=True)
		logging.info("\tCopying {} to {}".format(folder_names['cursors'], install_cursors_dir))
		shutil.copytree(folder_names['cursors'],install_cursors_dir,symlinks=True,ignore_dangling_symlinks=True)
		logging.info("\tCopying {} to {}".format(folder_names['theme'], install_themes_dir))
		shutil.copytree(folder_names['theme'],install_themes_dir,symlinks=True,ignore_dangling_symlinks=True)
		logging.info("\tCopying {} to {}".format(theme_wallpaper, str(Path.home())+"/Pictures/" ))
		shutil.copy(theme_wallpaper, str(Path.home())+"/Pictures/")
		for i in fonts:
			if not os.path.exists( str(Path.home())+"/.fonts/"+os.path.split(i)[1]):
				logging.info("\tCopying {} to {}".format(i, str(Path.home())+"/.fonts/" ))
				shutil.copy(i, str(Path.home())+"/.fonts/")
		font = lfcaptionfont
		if font == "MS Sans Serif":
			font = "Sans Serif"
		font = font + " " + weight[3:].lower().capitalize() + " 8"
		print("[Updating XFCE]")
		xfconf_item = [
		["xsettings","/Gtk/CursorThemeName", theme_name+"_Cursors", "Cursors" ],
		["xsettings","/Net/IconThemeName", theme_name+"_Icons", "Icons" ],
		["xsettings","/Net/ThemeName", theme_name+"_Theme", "Theme" ],
		["xfwm4","/general/theme", theme_name+"_Theme", "Windows Manager" ],
		["xfwm4","/general/title_font", font, "Font" ]
		]
		xfconf_query_path = subprocess.check_output(["which", "xfconf-query"]).strip()
		for i in xfconf_item:
			logging.info("\tChanging {} to {}".format(i[3], i[2]))
			args = [
				xfconf_query_path,
				"-c", i[0],
				"-p", i[1],
				"-s", i[2]
			]
			logging.debug(args)
			subprocess.check_call(args, stdout=subprocess.DEVNULL)
		print("Done!")

		print("\n{}\n".format("=-" * 40))
		print("The Microsoft theme {} is installed!\n".format(theme_name))
	else:
		font = lfcaptionfont
		print("\n[Skipped Install]\n\tTo install the theme {} run the following commands:\n".format(theme_name))
		print("\tcp -rav {} {}".format(folder_names['icons'], install_icons_dir))
		print("\tcp -rav {} {}".format(folder_names['cursors'], install_cursors_dir))
		print("\tcp -rav {} {}".format(folder_names['theme'], install_themes_dir))
		print("\tcp -rav {} {}".format(theme_wallpaper, str(Path.home())+"/Pictures/" ))
		for i in fonts:
			print("\tcp {} {}".format(i, str(Path.home())+"/.fonts/" ))
		print("\n\tThen change the icons, cursors, appearance and window manager to {}.\n\tThe theme font for window titles is: {}\n".format(theme_name, font))
	
	print("Thank you for using Chicago95 Plus!\n")

main()