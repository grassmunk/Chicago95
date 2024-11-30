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
# - Add a gui
# - Fix if missing colors
# Known Bugs:
# - If the theme is missing one of these colors the script will crash: ButtonDKShadow, ButtonLight, ButtonShadow, ButtonHilight, ButtonFace, ButtonText. Fix it by adding the missing color to the theme



import io
import os
import sys
import json
import struct
import shutil
import logging
import svgwrite
import PIL.Image
import subprocess
import configparser
import logging.handlers
import xml.etree.ElementTree as ET

from pathlib import Path
from pprint import pprint
from fontTools import ttLib
from configparser import ConfigParser
from PIL import BmpImagePlugin, PngImagePlugin, Image

running_folder = os.path.dirname(os.path.abspath(__file__))
share_dir = running_folder
libexec_dir = running_folder
work_dir = running_folder
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

SCREEN_SAVER_SCRIPT = '''#!/bin/sh

# *** DEPENDS ON xprintidle AND wmctrl AND wine ***
# From: https://joefreeman.weebly.com/using-windows-sreensavers-on-linux.html
# UNTESTED USE AT YOUR OWN RISK
# Screensaver to use
Screensaver="{scr_file}"

# Minutes to wait before activating
Timeout=10

#Convert minutes to milliseconds
IDLE_TIME=$(($Timeout*60*1000))

# Clobber normal Linux Screensaver and screen-blanking.
xset s off -dpms

sleep_time=$IDLE_TIME
triggered=false

# ceil() instead of floor()
while sleep $(((sleep_time+999)/1000)); do
  idle=$(xprintidle)
    if [ $idle -ge $IDLE_TIME ]; then
      if ! $triggered; then
        # Get a list of open windows and count the number of times YouTube &c is on it.
        youtube=`wmctrl -l|egrep -c 'YouTube|My5|All 4'`
        if [ $youtube -ge 1 ]; then 
          triggered=false
          sleep_time=$IDLE_TIME
        else
          wine $Screensaver /s
          triggered=true
          sleep_time=$IDLE_TIME
        fi
      fi
    else
      triggered=false
      # Give 100 ms buffer to avoid frantic loops shortly before triggers.
      sleep_time=$((IDLE_TIME-idle+100))
    fi'''


#ChicagoPlus Class
# Input:
#  - themefile: Full path to a Micosoft Windows .theme file 
#  - colors/overlap/squaresize: determines how inkscape creates scaled icons from ICO files. Less colors == faster.
#  - installdir: the director to install the converted theme to, decaults to current working directory
#  - chicago95_cursor_path/chicago95_theme_path/chicago95_icons_path: This class needs Chicago95 icons/themes/cursor folders to convert from
#                                                                     the default is set to the install locations for these themes
#  - loglevel: the current log level based on python logging to display to STDOUT
#  - logfile: file which will house debug log


class ChicagoPlus:
	def __init__(self, themefile, colors=32, overlap=1, 
			squaresize=20, installdir=os.getcwd(), 
			chicago95_cursor_path=str(Path.home())+"/.icons/Chicago95_Cursor_Black",
			chicago95_theme_path=str(Path.home())+"/.themes/Chicago95",
			chicago95_icons_path=str(Path.home())+"/.icons/Chicago95",
			loglevel=logging.WARNING,
			logfile='plus.log'):

		self.theme_file = themefile
		self.max_colors = colors
		self.overlap = overlap
		self.squaresize = squaresize
		self.installdir = installdir
		self.path_to_theme=''
		self.theme_file_name=''
		self.theme_name_spaces=''
		self.theme_ext=''
		self.theme_name = ''
		self.new_theme_folder=''
		self.chicago95_cursor_folder = chicago95_cursor_path
		self.chicago95_theme_folder = chicago95_theme_path
		self.chicago95_icons_folder = chicago95_icons_path

		# Placeholder for inkscape version and path information. It will be populated with actual information after it is confirmed that the user has Inkscape
		self.inkscape_info = inkscape_info("void", [0,0,0])
		
		 
		# Create the Logger
		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)
		#logger_formatter = logging.Formatter('%(name)s :: %(levelname)s :: %(message)s')
		logger_formatter = logging.Formatter('%(levelname)-8s :: %(funcName)-22s :: %(message)s')
		# Log everything to the log file
		fh = logging.FileHandler(logfile, mode='w')
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(logger_formatter)
		# Log whatever we get passed to stderr
		ch = logging.StreamHandler()
		ch.setFormatter(logger_formatter)
		ch.setLevel(loglevel)
		# Add the Handler to the Logger
		self.logger.addHandler(fh)
		self.logger.addHandler(ch)
		self.logger.debug("Theme File: {}".format(self.theme_file))
		self.logger.debug("Install directory: {}".format(self.installdir))
		self.logger.debug("Convert icon colors: {}, overlap: {}, squaresize: {}".format(self.max_colors, self.overlap, self.squaresize))

	def set_installdir(self, new_install_directory):
		self.logger.debug("Changing install directory to: {}".format(new_install_directory))
		self.installdir = new_install_directory

	def go(self, cursors=True, icons=True, wallpaper=True, sounds=True, colors=True, fonts=True, screensaver=True):
		self.logger.info("Starting Chicago Plus! with the folowing settings: cursors={}, icons={}, wallpaper={}, sounds={}, colors={}, fonts={}, screensaver={}".format(cursors, icons, wallpaper, sounds, colors, fonts, screensaver))
		self.check_software(cursors, icons, colors)
		self.parse_theme()
		self.generate_theme(cursors, icons, wallpaper, sounds, colors, fonts, screensaver)
		self.install_theme(cursors, icons, wallpaper, sounds, colors, fonts, screensaver)
		self.enable_theme(cursors, icons, wallpaper, sounds, colors, fonts, screensaver)
	
	def check_software(self, cursors=True, icons=True, colors=True):
		self.logger.info("Checking for required installed software")

		error = False
		if icons: 
			if not os.path.exists(self.chicago95_icons_folder):
				self.logger.critical("Either the Chicago95 or Chicago95_tux icon theme must be installed to {} to use this library".format(str(Path.home())+"/.icons/"))
				error = True
			try:
				inkscape_path = subprocess.check_output(["which", "inkscape"]).strip()
				#Assuming the previous portion doesn't return an exception, the placeholder information is replaced
				self.get_inkscape_info()
			except subprocess.CalledProcessError:
				self.logger.critical("You need inkscape installed to use this library.")
				error = True
		if cursors:

			if not os.path.exists(self.chicago95_cursor_folder):
				self.logger.critical("The Chicago95 cursor Chicago95_Cursor_Black must be installed to {} to use this library".format(str(Path.home())+"/.icons/"))
				error = True

			try:
				convert_path = subprocess.check_output(["which", "xcursorgen"]).strip()
			except subprocess.CalledProcessError:
				self.logger.critical("You need xcursorgen installed to use this library.")
				error = True

		if colors:
			if not os.path.exists(self.chicago95_theme_folder):
				self.logger.critical("The Chicago95 theme must be installed to {} to use this library".format(str(Path.home())+"/.themes/"))
				error = True

			try:
				convert_path = subprocess.check_output(["which", "convert"]).strip()
			except subprocess.CalledProcessError:
				self.logger.critical("You need imagemagick (convert) installed to use this library.")
				error = True

			try:
				convert_path = subprocess.check_output(["which", "mogrify"]).strip()
			except subprocess.CalledProcessError:
				self.logger.critical("You need imagemagick (mogrify) installed to use this library.")
				error = True

		if error:
			sys.exit(-1)


	def parse_theme(self):
		# This function takes the theme file passed at object instanciation and converts it to an easier to parse JSON file
		# Also fixes disparities between theme file case and filename case
		# Tries to fix 8 char limit as well

		self.theme_paths()
		self.read_theme_file()
		self.parse_icons()
		icons = self.icons
		for i in self.icons:
			if self.icons[i]:
				ico_filename = self.icons[i][0]
				index = self.icons[i][1]
				ico_file_path = self.get_actual_path(ico_filename)
				icons[i] = { 
					'filename' : ico_filename, 
					'index' : index, 
					'path' : ico_file_path,
					'type' : os.path.splitext(ico_filename)[1][1:]
				}
		
		self.parse_cursors()
		self.parse_wallpaper()
		self.parse_sound_files()
		self.parse_nonclientmetrics()
		self.parse_iconmetrics()
		self.parse_colors()		
		self.parse_screensaver()
		self.parse_font_files()
		if self.screensaver:		
			scr = self.get_actual_path(self.screensaver)
		else:
			scr = False
		self.find_all_wallpapers()

		self.theme_config = {
			'theme_name' : os.path.splitext(self.theme_file_name)[0],
			'theme_file' : self.theme_file,
			'installdir' : self.installdir,
			'icons'      : icons,
			'cursors'    : self.cursors,
			'fonts'      : self.fonts,
			'wallpaper'  : {'theme_wallpaper': self.wallpaper, 'extra_wallpapers' : self.extra_wallpapers},
			'colors'     : self.colors,
			'nonclientmetrics' : self.nonclientmetrics,
			'iconmetrics' : self.iconmetrics,
			'sounds':  self.sounds,
			'screensaver': scr,
			'all_files': self.theme_files
		}
		#if logging.getLogger(__name__).getEffectiveLevel() == logging.DEBUG:
		#	self.logger.debug("Printing current theme config")
		#	self.print_theme_config()

	def generate_theme(self, cursors=True, icons=True, wallpaper=True, sounds=True, colors=True, fonts=True, screensaver=True):

		self.install_folders()

		self.create_folders()

		if cursors:
			self.create_cursors()
		if icons:
			self.create_icons()
		if wallpaper:
			self.generate_wallpaper()
		if sounds:
			self.generate_sounds()
		if colors:
			self.convert_colors()
		if fonts:
			self.generate_fonts()
		if screensaver:
			self.generate_screensaver()

		self.dump_json(self.new_theme_folder+self.theme_name+".json")

	def dump_json(self, json_file_target='windows_theme.json'):
		self.logger.info("Dumping {} to JSON file {}".format(self.theme_file, json_file_target))
		with open(json_file_target, 'w') as outfile:
			json.dump(self.theme_config, outfile)
		self.logger.debug("Done".format(self.theme_file, json_file_target))
		
	def print_theme_config(self):
		self.logger.info("Print {} to JSON config".format(self.theme_file))
		pprint(self.theme_config)


	def get_actual_path(self, filename):
		# function to get the actual path, thanks windows caselessness
		if not filename:
			return False
		self.logger.debug("Finding '{}'".format(filename))
		if not os.path.exists(self.path_to_theme + filename.rstrip('\x00')):
			try:			
				actual_file_path = [self.theme_files[i] for i in self.theme_files if filename.lower() in i][0]
			except IndexError:
				actual_file_path = False
		else:
			actual_file_path = self.path_to_theme + filename
		self.logger.debug("Path to '{}': {}".format(filename, actual_file_path))
		return(actual_file_path)
		

#### Theme Parser functions

	def theme_paths(self):
		# There's a few ways theme files come packaged
		# 1) All the files in one folder
		# 2) The .theme file in one folder and everything else in a sub folder
		# 3) A folder with Program Files/Plus!/Themes/<files> and WINDOWS/SYSTEM
		# This method tries to find all the files/folders no matter what		
		
		self.logger.debug("Using file {}".format(self.theme_file))
		self.path_to_theme, self.theme_file_name = os.path.split(self.theme_file)
		if len(self.path_to_theme) != 0:
			self.path_to_theme = self.path_to_theme + "/"
		else:
			self.path_to_theme = "./"

		theme_name_spaces, theme_ext = os.path.splitext(self.theme_file_name)

		self.index_theme_name = theme_name_spaces + " (Chicago 95 Variant)" # For various Index.theme files
		self.theme_name = theme_name_spaces.capitalize().replace(" ", "_")
		if self.installdir[-1] != "/": 
			self.new_theme_folder = self.installdir + "/" + self.theme_name + "_Chicago95/"
		else:
			self.new_theme_folder = self.installdir + self.theme_name + "_Chicago95/"
		self.logger.debug("Path to theme: {}, theme file name: {}".format(self.path_to_theme, self.theme_file_name))
		if "Program Files/Plus!/Themes/".lower() in self.path_to_theme.lower():
			paths = self.splitall(self.path_to_theme)
			self.path_to_theme = ('/'.join(paths[0:-4])) + "/"
		
		if self.path_to_theme[0:2] == "//":
			self.path_to_theme = self.path_to_theme[1:]

		self.logger.debug("Path to theme: {}, theme file name: {}".format(self.path_to_theme, self.theme_file_name))
		self.logger.debug("New theme folder: {}".format(self.new_theme_folder))
		
		# we use thise dict to remove case but keep the filenames
		self.theme_files = {}
		self.logger.debug("Files in theme directory {}".format(self.path_to_theme))
		for root, dirs, files in os.walk(self.path_to_theme, topdown=False):
			for name in files:
				self.theme_files[os.path.join(root, name).lower()] = os.path.join(root, name)
				self.logger.debug(self.theme_files[os.path.join(root, name).lower()])

	def read_theme_file(self):

		if os.stat(self.theme_file).st_size == 0:
			self.logger.critical("Theme file {} is empty".format(self.theme_file))
			sys.exit(-1)

		if not os.path.exists(self.theme_file):
			self.logger.critical("Theme file {} does not exist".format(self.theme_file))
			sys.exit(-1)

		self.config = ConfigParser(interpolation=None)
		try:
			self.config.read(self.theme_file)
		except UnicodeDecodeError:
			try:
				self.config.read(self.theme_file, encoding='iso-8859-14')
			except configparser.DuplicateSectionError as w:
				self.logger.critical("Error reading {}. Remove duplicate section to use this theme. Error: {}".format(self.theme_file, w))
				sys.exit(-1)
			except configparser.DuplicateOptionError as w:
				self.logger.critical("Error reading {}. Remove duplicate options to use this theme. Error: {}".format(self.theme_file, w))
				sys.exit(-1)
			except configparser.MissingSectionHeaderError as w:
				self.logger.critical("Error reading {}. Make sure all comments start with ; in the theme file and reload this theme. Error: {}".format(self.theme_file, w))
				sys.exit(-1)
			except configparser.ParsingError as w:
				self.logger.critical("Error reading {}. Error: {}".format(self.theme_file, w))
				sys.exit(-1)
		except configparser.DuplicateSectionError as w:
			self.logger.critical("Error reading {}. Remove duplicate section to use this theme. Error: {}".format(self.theme_file, w))
			sys.exit(-1)
		except configparser.DuplicateOptionError as w:
			self.logger.critical("Error reading {}. Remove duplicate options to use this theme. Error: {}".format(self.theme_file, w))
			sys.exit(-1)
		except configparser.MissingSectionHeaderError as w:
			self.logger.critical("Error reading {}. Make sure all comments start with ; in the theme file and reload this theme. Error: {}".format(self.theme_file, w))
			sys.exit(-1)
		except configparser.ParsingError as w:
			self.logger.critical("Error reading {}. Error: {}".format(self.theme_file, w))
			sys.exit(-1)

		#except:
		#	print("Error reading theme file: {}".format(self.theme_file))
		#	print("Usually this is because of comments missing the ; on the first line.")
		#	sys.exit(-1)

	def parse_icons(self):
		self.logger.info("Parsing Icons")
		self.icons = {}

		self.icons["my_computer"]  = self.get_icon_file_name("CLSID\\{20D04FE0-3AEA-1069-A2D8-08002B30309D}\\DefaultIcon","DefaultValue")

		if self.get_file_name("CLSID\\{450D8FBA-AD25-11D0-98A8-0800361B1103}\\DefaultIcon","DefaultValue"):
			self.icons["my_documents"] = self.get_icon_file_name("CLSID\\{450D8FBA-AD25-11D0-98A8-0800361B1103}\\DefaultIcon","DefaultValue")
		elif self.get_file_name("CLSID\\{59031A47-3F72-44A7-89C5-5595FE6B30EE}\\DefaultIcon","DefaultValue"):
			self.icons["my_documents"] = self.get_icon_file_name("CLSID\\{59031A47-3F72-44A7-89C5-5595FE6B30EE}\\DefaultIcon","DefaultValue")
		else:
			self.icons["my_documents"] = False

		if self.get_file_name("CLSID\\{208D2C60-3AEA-1069-A2D7-08002B30309D}\\DefaultIcon","DefaultValue"):
			self.icons["network_neighborhood"] = self.get_icon_file_name("CLSID\\{208D2C60-3AEA-1069-A2D7-08002B30309D}\\DefaultIcon","DefaultValue")
		elif self.get_file_name("CLSID\\{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}\\DefaultIcon","DefaultValue"):
			self.icons["network_neighborhood"] =  self.get_icon_file_name("CLSID\\{F02C1A0D-BE21-4350-88B0-7367FC96EF3C}\\DefaultIcon","DefaultValue")
		else:
			self.icons["network_neighborhood"] = False

		self.icons["recycle_bin_full"]  = self.get_icon_file_name("CLSID\\{645FF040-5081-101B-9F08-00AA002F954E}\\DefaultIcon","Full")

		self.icons["recycle_bin_empty"] = self.get_icon_file_name("CLSID\\{645FF040-5081-101B-9F08-00AA002F954E}\\DefaultIcon","Empty")

		self.logger.debug("{:<21} {}".format('Type', 'Icon Name'))
		for i in self.icons:
			self.logger.info("{:<21} | {}".format(i,self.icons[i]))

	def parse_colors(self):
		self.logger.info("Parsing Control Panel\Colors")

		color_desc = {
			# From:
			# 	https://www.neowin.net/forum/topic/624901-windows-colors-explained/
			# 	https://web.archive.org/web/20151019120141/https://www.neowin.net/forum/topic/624901-windows-colors-explained/

			# Text Colors
			'buttontext': 'shown on 3D Buttons',
			'graytext': 'Unknown, MS documentation is inaccurate',
			'hottrackingcolor': 'active text, such as a link',
			'menutext': 'shown on the MenuBar and Menus',
			'windowtext': 'the main text inside a window',

			# Selection
			'hilight': 'background color of a selection',
			'highlight': 'background color of a selection',
			'hilighttext': 'foreground text color of the selection',
			'highlighttext': 'foreground text color of the selection',
			'menuhilight': 'background color of a selection on a menu',

			# Active Caption Bar (i.e. focused window title bar)
			'activetitle': 'Title bar active color',
			'titletext': 'Title bar text color for active windows',
			'gradientactivetitle': 'Windows 98 second color gradient on right',

			# Inactive Caption Bar
			'inactivetitle': 'Title bar color for inactive windows',
			'inactivetitletext': 'Title bar text color for inactive windows',
			'gradientinactivetitle': 'Windows 98 one of two colors, this is the right gradient',

			# Tooltip
			'infotext': 'tooltip text color',
			'infowindow': 'the color of the tooltip itself (default is a light yellow)',

			# Windows 3D Colors (the 4, one pixel wide, colors on every button/windows/etc that provide the 3d look)
			'buttonface': 'main button color',
			'buttonlight': 'top/left inside',
			'buttondkshadow': 'bottom/right outside',
			'buttonhilight': 'top/left outside',
			'buttonhighlight': 'top/left outside',
			'buttonshadow': 'bottom/right inside',

			# Other Window Colors
			'activeborder': ' border of the active window, drawn inside the 3D colors',
			'inactiveborder': 'border of the inactive window, drawn inside the 3D colors',
			'menu': 'color of a menu, overrides the ButtonFace attribute',
			'menubar': 'color of the menubar, unused by Plus!',
			'scrollbar': 'color of the scrollbar TRACK, scrollbar itself drawn using 3D Button attributes',
			'window': ' main background color inside a window, typically white',
			'windowframe': 'typically the single line border seen around active buttons',
			'appworkspace': 'background color in an application that may contain windows, such as GIMP',
			'background': 'desktop area, with no wallpaper applied',
			'buttonalternateface' : "Unknown",
			'messageboxtext': 'Text in a messagebox, unused by Plus!',
			'messagebox': 'messagebox, unused by Plus!'
		}

		self.colors = {}

		if "Control Panel\Colors" in self.config:
			for color_name in self.config["Control Panel\Colors"]:
				if len(self.config["Control Panel\Colors"][color_name].split()) > 2:
					r, g, b = self.config["Control Panel\Colors"][color_name].split()
					self.colors[color_name] = {'color': '#{:02x}{:02x}{:02x}'.format(int(r),int(g),int(b)), 'description' : color_desc[color_name] }
					self.logger.info("{:<21} | {:<7} ({:<11}) desc: {}".format(color_name, self.colors[color_name]['color'], self.config["Control Panel\Colors"][color_name],self.colors[color_name]['description']))

	def parse_cursors(self):
		self.logger.info("Parsing Control Panel\Cursors")
		self.cursors = {}
		if "Control Panel\Cursors" in self.config:
			for cursor_name in self.config["Control Panel\Cursors"]:		
				if self.get_file_name("Control Panel\Cursors",cursor_name):
					cur_type = os.path.splitext(self.get_file_name("Control Panel\Cursors",cursor_name))[1][1:]
					self.cursors[cursor_name] =  { 
						'type' : cur_type , 
						'filename': self.get_file_name("Control Panel\Cursors",cursor_name),
						'path' : self.get_actual_path(self.get_file_name("Control Panel\Cursors",cursor_name))}
				else:
					self.cursors[cursor_name] = False
				self.logger.info("{:<21} | {}".format(cursor_name, self.cursors[cursor_name]))


	def parse_sound_files(self):
		## Get Sound files
		self.logger.info("Parsing sounds")
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

		self.sounds = {}
		for i in sound_names:
			sound_name = i.split("\\")[-2]
			if self.get_file_name(i,"DefaultValue"):
				wav_file = self.get_file_name(i,"DefaultValue")
				self.sounds[sound_name] = self.get_actual_path(wav_file)
				self.logger.info("{:<21} | {}".format(sound_name, wav_file))

	def parse_screensaver(self):
		#Screen Saver
		self.screensaver = False
		if "boot" in self.config:
			self.logger.info("Parsing Boot (screensaver)")
			self.screensaver = self.get_file_name("boot","SCRNSAVE.EXE", True)
			self.logger.info("{:<21} | {}".format("screensaver",self.screensaver))
		
	def parse_wallpaper(self):## Get the wallpaper
		self.wallpaper = False

		
		if "Control Panel\Desktop" in self.config:
			self.wallpaper = {'wallpaper' : False, "tilewallpaper": False, "wallpaperstyle" : 0, 'filename': ''}
			self.logger.info("Parsing Control Panel\Desktop Wallpaper")
			self.wallpaper['wallpaper'] = self.get_file_name("Control Panel\Desktop","Wallpaper", ignore_windir=True)
			# TileWallpaper=0
			#  0: The wallpaper picture should not be tiled 
			#  1: The wallpaper picture should be tiled 
			
			if self.config.has_option("Control Panel\Desktop",'tilewallpaper') and self.config["Control Panel\Desktop"]["tilewallpaper"] != '0':
				self.wallpaper['tilewallpaper'] = True
			if self.config.has_option("Control Panel\Desktop", "wallpaperstyle"):			
				if isinstance(self.config["Control Panel\Desktop"]["wallpaperstyle"], list):
					self.wallpaper["wallpaperstyle"] = self.config["Control Panel\Desktop"]["wallpaperstyle"][0]
				else:
					self.wallpaper["wallpaperstyle"] = self.config["Control Panel\Desktop"]["wallpaperstyle"]
			
			
			# WallpaperStyle=2
			#; 0:  The image is centered if TileWallpaper=0 or tiled if TileWallpaper=1
			#; 2:  The image is stretched to fill the screen
			#; 6:  The image is resized to fit the screen while maintaining the aspect 
			#      ratio. (Windows 7 and later)
			#; 10: The image is resized and cropped to fill the screen while maintaining 
			#      the aspect ratio. (Windows 7 and later)

			if self.wallpaper['wallpaper']:
				self.wallpaper['path'] = self.get_actual_path(self.wallpaper['wallpaper'])
				try:
					self.wallpaper['wallpaperstyle'] = int(self.wallpaper['wallpaperstyle'])
				except ValueError:
					self.wallpaper['wallpaperstyle'] = 2					

				self.wallpaper['new_filename'] = (os.path.splitext(self.wallpaper['wallpaper'])[0] + "_" + 
								str(int(self.wallpaper['tilewallpaper'])) + "_" + 
								str(int(self.wallpaper['wallpaperstyle'])) + os.path.splitext(self.wallpaper['wallpaper'])[1])
			for i in self.wallpaper:
				self.logger.info("{:<21} | {}".format(i,self.wallpaper[i]))

	def parse_font_files(self):
		self.logger.debug("Parsing Font files")
		# First find font files
		self.fonts = {}
		fonts = [self.theme_files[i] for i in self.theme_files if "ttf" in i] 
		for font in fonts:
			self.logger.info("Parsing font file: {}".format(font))
			try: 
				ttf = ttLib.TTFont(font)
			except ttLib.TTLibError as error:
				self.logger.error("Font {} cannot be read: {}".format(font, error))
				return

			name, family =  self.font_name(ttf)
			self.fonts[family] = { "name" : name, "family" : family, 'path': font } 
		for i in self.fonts:
			self.logger.info("{:<21} | {}".format("Font file:", i))
			self.logger.info("{:<21} | {}".format("Font name:", self.fonts[i]['name']))
			self.logger.info("{:<21} | {}".format("Font family:", self.fonts[i]['family']))
	

	def parse_nonclientmetrics(self):
		self.logger.info("Parsing NonClientMetrics")
		self.nonclientmetrics = False
		if 'Metrics' not in self.config:
			return

		if 'NonClientMetrics' not in self.config['Metrics']:
			return

		if len(self.config["Metrics"]["NonClientMetrics"]) <= 1:
			return
		
		NONCLIENTMETRICSA = self.config["Metrics"]["nonclientmetrics"]
		
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
			"1000":"FW_BLACK"
			
		}

		x = []
		for i in NONCLIENTMETRICSA.split():
			if(int(i)) > 256:
				self.logger.error("NonClientMetrics has a byte larger than 255, cannot parse NonClientMetrics!")
				return
			x.append(int(i))


		self.nonclientmetrics = {
		"cbSize" 	: int.from_bytes(x[0:4],"little"),
		"iBorderWidth"	: int.from_bytes(x[4:8],"little"),
		"iScrollWidth"	: int.from_bytes(x[8:12],"little"),
		"iScrollHeight"	: int.from_bytes(x[12:16],"little"),
		"iCaptionWidth"	: int.from_bytes(x[16:20],"little"),
		"iCaptionHeight": int.from_bytes(x[20:24],"little")
		}
		self.nonclientmetrics['lfcaptionfont'] = { # This is the font used for titlebars
		"desc:" : "Font used for windows title bar (captions)",
		"lfHeight" : int.from_bytes(x[24:28],"little", signed=True),
		"lfWidth" : int.from_bytes(x[28:32],"little"),
		"lfEscapement" : int.from_bytes(x[32:36],"little"),
		"lfOrientation" : int.from_bytes(x[36:40],"little"),
		"lfWeight" : font_weight[str(int(round(int.from_bytes(x[40:44],"little"),-2)))],
		"lfItalic" : x[44],
		"lfUnderline" : x[45],
		"lfStrikeOut" : x[46],
		"lfCharSet" :  x[47],
		"lfOutPrecision" : x[48],
		"lfClipPrecision" : x[49],
		"lfQuality" : x[50],
		"lfPitchAndFamily" : x[51],
		 "lfFaceName[32]" : self.null_string(x[52:52+32])
		}

		self.nonclientmetrics["iSmCaptionWidth"] = int.from_bytes(x[84:88],"little")
		self.nonclientmetrics["iSmCaptionHeight"] = int.from_bytes(x[88:92],"little")

		self.nonclientmetrics['lfSmCaptionFont'] = { # This is used for docked title bars
		"desk" : "Font used for docked windows title bar (small caption)",
		"lfHeight" : int.from_bytes(x[92:96],"little", signed=True),
		"lfWidth" : int.from_bytes(x[96:100],"little"),
		"lfEscapement" : int.from_bytes(x[100:104],"little"),
		"lfOrientation" : int.from_bytes(x[104:108],"little"),
		"lfWeight" : font_weight[str(int(round(int.from_bytes(x[108:112],"little"),-2)))],
		"lfItalic" : x[112],
		"lfUnderline" : x[113],
		"lfStrikeOut" : x[114],
		"lfCharSet" :  x[115],
		"lfOutPrecision" : x[116],
		"lfClipPrecision" : x[117],
		"lfQuality" : x[118],
		"lfPitchAndFamily" : x[119],
		 "lfFaceName[32]" : self.null_string(x[120:120+32])
		}

		self.nonclientmetrics["iMenuWidth"] = int.from_bytes(x[152:156],"little")
		self.nonclientmetrics["iMenuHeight"] = int.from_bytes(x[156:160],"little")

		self.nonclientmetrics['lfMenuFont'] = { # The font used in menus
		"desc" : "Font used in menus",
		"lfHeight" : int.from_bytes(x[160:164],"little", signed=True),
		"lfWidth" : int.from_bytes(x[164:168],"little"),
		"lfEscapement" : int.from_bytes(x[168:172],"little"),
		"lfOrientation" : int.from_bytes(x[172:176],"little"),
		"lfWeight" : font_weight[str(int(round(int.from_bytes(x[176:180],"little"),-2)))],
		"lfItalic" : x[180],
		"lfUnderline" : x[181],
		"lfStrikeOut" : x[182],
		"lfCharSet" :  x[183],
		"lfOutPrecision" : x[184],
		"lfClipPrecision" : x[185],
		"lfQuality" : x[186],
		"lfPitchAndFamily" : x[187],
		 "lfFaceName[32]" : self.null_string(x[188:188+32])
		}

		self.nonclientmetrics['lfStatusFont'] = { # Status bars and tooltips font
		"desc" : "Font used in status bars and tooltips",
		"lfHeight" : int.from_bytes(x[220:224],"little", signed=True),
		"lfWidth" : int.from_bytes(x[224:228],"little"),
		"lfEscapement" : int.from_bytes(x[228:232],"little"),
		"lfOrientation" : int.from_bytes(x[232:236],"little"),
		"lfWeight" : font_weight[str(int(round(int.from_bytes(x[236:240],"little"),-2)))],
		"lfItalic" : x[240],
		"lfUnderline" : x[241],
		"lfStrikeOut" : x[242],
		"lfCharSet" :  x[243],
		"lfOutPrecision" : x[244],
		"lfClipPrecision" : x[245],
		"lfQuality" : x[246],
		"lfPitchAndFamily" : x[247],
		 "lfFaceName[32]" : self.null_string(x[248:248+32])
		}

		self.nonclientmetrics['lfMessageFont'] = { # Text in message boxes font
		"desc" : "Font used in message boxes",
		"lfHeight" : int.from_bytes(x[280:284],"little", signed=True),
		"lfWidth" : int.from_bytes(x[284:288],"little"),
		"lfEscapement" : int.from_bytes(x[288:292],"little"),
		"lfOrientation" : int.from_bytes(x[292:296],"little"),
		"lfWeight" : font_weight[str(int(round(int.from_bytes(x[296:300],"little"),-2)))],
		"lfItalic" : x[300],
		"lfUnderline" : x[301],
		"lfStrikeOut" : x[302],
		"lfCharSet" :  x[303],
		"lfOutPrecision" : x[304],
		"lfClipPrecision" : x[305],
		"lfQuality" : x[306],
		"lfPitchAndFamily" : x[307],
		 "lfFaceName[32]" : self.null_string(x[308:308+32])
		}
		self.logger.debug("[nonclientmetrics]")
		for i in self.nonclientmetrics:
			if i in ['lfcaptionfont','lfMessageFont','lfStatusFont','lfMenuFont','lfSmCaptionFont']:
				for j in self.nonclientmetrics[i]:
					self.logger.debug("{:<21} | {:<21} | {}".format(i, j, self.nonclientmetrics[i][j]))
			else:
				self.logger.debug("{:<21} | {}".format(i, self.nonclientmetrics[i]))
	

		#return lfcaptionfont["lfFaceName[32]"], lfcaptionfont["lfWeight"]

	def parse_iconmetrics(self):
		self.logger.info("Parsing IconMetrics")
		self.iconmetrics = False
		
		if not self.config.has_section('Metrics'):
			return

		if 'IconMetrics' not in self.config['Metrics']:
			return

		if len(self.config["Metrics"]["IconMetrics"]) <= 1:
			return
		
		IconMetrics = self.config["Metrics"]["iconmetrics"]
	
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
			if(int(i)) > 256:
				self.logger.error("IconMetrics has a byte larger than 255, cannot parse IconMetrics")
				return
			x.append(int(i))

	 
		self.iconmetrics = {
		"cbSize" 	: int.from_bytes(x[0:4],"little"),
		"iHorzSpacing"	: int.from_bytes(x[4:8],"little"),
		"iVertSpacing"	: int.from_bytes(x[8:12],"little"),
		"iTitleWrap"	: int.from_bytes(x[12:16],"little")
		}

		self.iconmetrics['lfFont'] = {
		"desc:" : "Font used to display icons",
		"lfHeight" : int.from_bytes(x[16:20],"little", signed=True),
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
		 "lfFaceName[32]" : self.null_string(x[44:44+32])
		}
		self.logger.debug("[iconmetrics]")
		for i in self.iconmetrics:
			if i in ['lfFont']:
				for j in self.iconmetrics[i]:
					self.logger.debug("{:<21} | {:<21} | {}".format(i, j, self.iconmetrics[i][j]))
			else:
				self.logger.debug("{:<21} | {}".format(i, self.iconmetrics[i]))
	

#### Generator Functions 	
	def install_folders(self):
		self.chicago95_cursor_folder
		self.chicago95_theme_folder
		self.chicago95_icons_folder

		self.folder_names = {
			"root"    : self.new_theme_folder,
			"icons"   : self.new_theme_folder + self.theme_name + "_Icons/",
			"theme"   : self.new_theme_folder + self.theme_name + "_Theme/",
			"cursors" : self.new_theme_folder + self.theme_name + "_Cursors/",
			"sounds"  : self.new_theme_folder + self.theme_name + "_Sounds/",
			"screensaver"  : self.new_theme_folder + self.theme_name + "_Screensaver/",
			"fonts"  : self.new_theme_folder + self.theme_name + "_Fonts/"
			 }

		self.logger.info("Install folder names")
		for i in self.folder_names:
			self.logger.info("{:<21} | {}".format(i, self.folder_names[i]))

	def create_folders(self, delete=True):
		for i in self.folder_names:
	
			if delete:
				self.logger.debug("Deleting {} previous folder {}".format(i,self.folder_names[i]))	
				shutil.rmtree(self.folder_names[i], ignore_errors=True)

			self.logger.debug("Creating {} folder: {}".format(i,self.folder_names[i]))	
			if i == "icons":
				shutil.copytree(self.chicago95_icons_folder,self.folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
			elif i == "cursors":
				shutil.copytree(self.chicago95_cursor_folder,self.folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
			elif i == "theme":
				shutil.copytree(self.chicago95_theme_folder,self.folder_names[i],symlinks=True,ignore_dangling_symlinks=True)
			else:
				os.mkdir(self.folder_names[i])

	def create_icons(self, create_48_document_icon = True):
		self.logger.info(f"Creating new icons in {self.folder_names['icons']}")

		svg_file_names = {}
		png_file_names = {
			 "my_computer"           : "user-home.png",
			 "my_documents"          : "folder-documents.png",
			 "network_neighborhood"  : "folder-remote.png",
			 "recycle_bin_empty"     : "user-trash.png",
			 "recycle_bin_full"      : "user-trash-full.png"
			 }

		for i in png_file_names:
			svg_file_names[i] = png_file_names[i].replace(".png", ".svg")

		for iconname in self.theme_config['icons']:
			self.logger.debug(f"Processing icon: {iconname}")
			self.logger.info(f"Processing icon: {iconname}")

			if not self.theme_config['icons'][iconname]:
				self.logger.warning(f"{iconname:<21} | Icon does not exist in this theme")
				continue

			icon_sizes = [16, 22, 24, 32, 48]

			filename = self.theme_config['icons'][iconname]['filename']
			index = self.theme_config['icons'][iconname]['index']
			path = self.theme_config['icons'][iconname]['path']
			filetype = self.theme_config['icons'][iconname]['type']

			self.logger.debug(f"Icon details - Name: {filename}, Index: {index}, Path: {path}, Type: {filetype}")

			if not path:
				self.logger.warning(f"{iconname:<21} | {filename} does not exist in this theme")
				continue

			if filetype not in ['dll', 'icl', 'ico', 'bmp']:
				self.logger.warning(f"File type {filetype} not supported: {filename}")
				continue

			self.logger.info(f"{iconname:<21} | {filename}")

			if filetype in ['dll', 'icl']:
				# Get the icons stored in the DLL
				self.logger.debug("{:<21} | Icons are stored in ICL file {}".format("", filename, path))
				icon_files = self.extract_icons_from_dll(path)
			else:
				self.logger.debug(f"{iconname:<21} | Icons are stored in ICO file {filename} {path}")
				icon_files = self.extract_ico(path)
				if icon_files == 'bmp':
					filetype = 'bmp'

			if not icon_files:
				self.logger.error(f"Not a valid icon file: {self.theme_config['icons'][iconname]}")
				continue

			# If the icons exist at various sizes, write them and convert them instead of scaling the largest one
			for size in icon_sizes:
				self.logger.debug(f"{iconname:<21} | Searching for icon size: {size} in {filename}")

				if filetype in ['dll', 'icl']:
					icon_filename, icon_file = self.get_icons_size_dll(icon_files, index, size)
				elif filetype == 'ico':
					icon_filename, icon_file = self.get_icons_size_ico(icon_files, size)
				else:
					icon_filename = False
				if icon_filename:
					icon_sizes.remove(size)
					destination = os.path.join(self.folder_names['icons'], icon_filename)
					with open(destination, "wb") as f:
						f.write(icon_file)
					sized_target = os.path.join(
						self.folder_names['icons'], "places", str(size), png_file_names[iconname]
					)
					self.logger.debug(f"{iconname:<21} | Creating: {size} {destination} {sized_target}")
					self.convert_ico_files(destination, sized_target)

			# Now that we're done, get the largest file and use that for the rest
			if filetype in ['dll', 'icl']:
				icon_filename, icon_file = self.get_largest_icon_dll(icon_files, index)
			elif filetype == 'ico':
				icon_filename, icon_file = self.get_largest_icon_ico(icon_files, size)

			if filetype in ['dll', 'icl', 'ico'] and not isinstance(icon_file, str):
				destination = os.path.join(self.folder_names['icons'], icon_filename)
				with open(destination, "wb") as f:
					f.write(icon_file)
			else:
				destination = os.path.join(self.folder_names['icons'], os.path.basename(icon_filename))
				shutil.copyfile(path, destination)

			svg_icon_file = self.convert_icon(self.folder_names['icons'], destination)
			for size in icon_sizes:
				if size <= 32 and iconname == "documents_ico" and not create_48_document_icon:
					continue
				sized_target = os.path.join(
					self.folder_names['icons'], "places", str(size), png_file_names[iconname]
				)
				self.logger.debug(f"{iconname:<21} | Creating: {size} {svg_icon_file} {sized_target}")
				self.convert_to_png_with_inkscape(svg_icon_file, size, sized_target)

			scaled_target = os.path.join(
				self.folder_names['icons'], "places", "scalable", svg_file_names[iconname]
			)
			shutil.copy(svg_icon_file, scaled_target)

		# Update index.theme
		self.logger.debug("Updating icon index.theme file")
		icon_theme_config = configparser.RawConfigParser(interpolation=None)
		icon_theme_config.optionxform = str
		icon_theme_config.read(os.path.join(self.folder_names['icons'], "index.theme"))
		icon_theme_config.set("Icon Theme", "Name", self.index_theme_name)
		with open(os.path.join(self.folder_names['icons'], "index.theme"), 'w') as configfile:
			icon_theme_config.write(configfile, space_around_delimiters=False)


	def create_cursors(self):
		self.logger.info("Creating new xcursors in {}".format(self.folder_names['cursors']))
		pointers = {
			#windows theme  # X11 Theme
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
			"sizenwse"    : "AngleNW",
			"sizenesw"    : "AngleNE",
			"sizeall"     : "SizeAll",
			"uparrow"     : "UpArrow"
			}


		cursor_src_folder = self.folder_names['cursors'] + "src/"
		self.logger.debug("Cursor source folder: {}".format(cursor_src_folder))
		tabs = 21
		for i in self.theme_config['cursors']:
			if self.theme_config['cursors'][i] and tabs < len(self.theme_config['cursors'][i]['filename']):
				tabs = len(self.theme_config['cursors'][i]['filename'])


		for current_cursor in pointers:
			self.logger.debug("Current cursor: {} ({cur}.conf/{cur}.png)".format(current_cursor, cur=pointers[current_cursor]))

			if (current_cursor not in self.theme_config['cursors'] or not 
			    self.theme_config['cursors'][current_cursor] or not 
			    self.theme_config['cursors'][current_cursor]['path']): 
				continue
			
			theme_cursor_config = self.theme_config['cursors'][current_cursor]

			self.logger.info("{:<21} | file: {}".format(current_cursor, theme_cursor_config['filename']))

			x11_cursor_file_name = cursor_src_folder+pointers[current_cursor]+".png" # Target Folder for converted cursors
			#os.remove(x11_cursor_file_name)
			
			self.logger.debug("{:<21} | {} --> {}".format("", theme_cursor_config['filename'],os.path.split(x11_cursor_file_name)[1]))

			if theme_cursor_config['type'] == 'ani':
				self.logger.debug("{:<21} | Cursor {} is type ani".format(current_cursor, theme_cursor_config['filename']))
				ani_file_config = self.extract_ani(theme_cursor_config['path'])
				#pprint(ani_file_config)
				self.logger.debug("{:<21} | Header - nFrames: {}, nSteps: {}, iDispRate: {}".format(current_cursor, ani_file_config['anih']['nFrames'], ani_file_config['anih']['nSteps'], ani_file_config['anih']['iDispRate']))
				write_conf = open(cursor_src_folder+pointers[current_cursor]+".conf", 'w')
				if ani_file_config['INFO']:
					
					ani_readme = open(cursor_src_folder+pointers[current_cursor]+".info", 'w')
					if 'INAM' in ani_file_config['INFO']: 
						ani_readme.write("Title: {}\n".format(ani_file_config['INFO']['INAM'].replace('\x00', '')))
						self.logger.debug("{:<21} | Artist name (INAM): {}".format(current_cursor, ani_file_config['INFO']['INAM'].replace('\x00', '')))
					if 'IART' in ani_file_config['INFO']: 
						ani_readme.write("Artist: {}\n".format(ani_file_config['INFO']['IART'].replace('\x00', '')))
						self.logger.debug("{:<21} | Artist details (IART): {}".format(current_cursor, ani_file_config['INFO']['IART'].replace('\x00', '')))
					ani_readme.write("Theme: {}".format(self.theme_name))
					ani_readme.close()
				if ani_file_config['seq']:
					for sequence in ani_file_config['seq']:
						if ani_file_config['rate']:
							rate = ani_file_config['rate'][sequence] * 17
						else:
							rate = ani_file_config['anih']['iDispRate'] * 17

						for icon in ani_file_config['icon']:
							if icon['index'] == sequence:
								xhot = icon['rtIconDirEntry']['wPlanes']
								yhot = icon['rtIconDirEntry']['wBitCount']
								size = icon['rtIconDirEntry']['bHeight']
								self.logger.debug("{:<21} | Sequence: {}, rate: {}, size: {}, xhot: {}, yhot: {}".format(current_cursor, sequence, rate, size,xhot, yhot))
								cur_filename = pointers[current_cursor]+"_"+str(sequence)
								f = open(cursor_src_folder+cur_filename+".cur","wb")
								f.write(icon['ico_file'])
								f.close()
								self.convert_cur_files(cursor_src_folder+cur_filename+".cur", cursor_src_folder+cur_filename+".png")
								write_conf.write("{size} {xhot} {yhot} {filename} {rate}\n".format(size=size, xhot=xhot, yhot=yhot, filename=cur_filename+".png", rate=rate ))
				else:
					for icon in ani_file_config['icon']:
						xhot = icon['rtIconDirEntry']['wPlanes']
						yhot = icon['rtIconDirEntry']['wBitCount']
						size = icon['rtIconDirEntry']['bHeight']
						rate = ani_file_config['anih']['iDispRate'] * 17
						self.logger.debug("{:<21} |  Sequence: {}, rate: {}, size: {}, xhot: {}, yhot: {}".format(current_cursor, icon['index'], rate, size,xhot, yhot))
						cur_filename = pointers[current_cursor]+"_"+str(icon['index'])
						f = open(cursor_src_folder+cur_filename+".cur","wb")
						f.write(icon['ico_file'])
						f.close()
						self.convert_cur_files(cursor_src_folder+cur_filename+".cur", cursor_src_folder+cur_filename+".png")
						write_conf.write("{size} {xhot} {yhot} {filename} {rate}\n".format(size=size, xhot=xhot, yhot=yhot, filename=cur_filename+".png", rate=rate))
				
				for icon in ani_file_config['icon']:
					xhot = icon['rtIconDirEntry']['wPlanes']
					yhot = icon['rtIconDirEntry']['wBitCount']
					size = icon['rtIconDirEntry']['bHeight']
					#print(xhot, yhot, size)
				write_conf.close()				

			elif theme_cursor_config['type'] in ['cur', 'ico']:
				self.logger.debug("{:<21} | Cursor {} is type cur".format(current_cursor, theme_cursor_config['filename']))
				cursor_file_config = self.extract_cur(theme_cursor_config['path'])
				xhot = cursor_file_config['icon'][0]['rtIconDirEntry']['wPlanes']
				yhot = cursor_file_config['icon'][0]['rtIconDirEntry']['wBitCount']
				size = cursor_file_config['icon'][0]['rtIconDirEntry']['bHeight']
				icon_file = cursor_file_config['icon'][0]['ico_file']
				f = open(cursor_src_folder+pointers[current_cursor]+".cur","wb")
				f.write(icon_file)
				f.close()
				try:
					self.convert_cur_files(cursor_src_folder+pointers[current_cursor]+".cur", cursor_src_folder+pointers[current_cursor]+".png")
					write_conf = open(cursor_src_folder+pointers[current_cursor]+".conf", 'w')
					self.logger.debug("{:<21} | Writting conf file {}: {size} {xhot} {yhot} {filename}".format(current_cursor, pointers[current_cursor]+".conf", size=size, xhot=xhot, yhot=yhot, filename=pointers[current_cursor]+".png"))
					write_conf.write("{size} {xhot} {yhot} {filename}".format(size=size, xhot=xhot, yhot=yhot, filename=pointers[current_cursor]+".png"))
					write_conf.close()				
				except:
					self.logger.critical("Error converting {}. Cursor file corrupt".format(cursor_src_folder+pointers[current_cursor]+".cur"))

		# Cursors are all done now we need to generate X11 cursors with xcursorgen
		self.build_cursors(self.folder_names['cursors'])
		cur_theme_config = configparser.RawConfigParser(interpolation=None)
		cur_theme_config.optionxform = str
		cur_theme_config.read(self.folder_names['cursors']+"index.theme")
		cur_theme_config.set("Icon Theme","Name",self.index_theme_name)
		with open(self.folder_names['cursors']+"index.theme", 'w') as configfile:
			cur_theme_config.write(configfile, space_around_delimiters=False)

	def convert_colors(self):
		windows_to_gtk = {
			'activeborder' : False,
			'activetitle' : 'window_title_bg_color',
			'appworkspace' : False,
			'background' : False,
			'buttondkshadow' : 'border_dark',
			'buttonface' : ['bg_color', 'border_color', 'button_bg_color'],
			'buttonlight' : 'border_light',
			'buttonhilight' : 'border_bright',
			'buttonshadow' : 'border_shade',
			'buttontext' :  'button_text_color',
			'graytext' : 'selected_bg_color',
			'hilight' : 'selected_bg_color',
			'hilighttext' : 'selected_fg_color',
			'inactiveborder' : False,
			'inactivetitle' : 'inactive_title_bg_color',
			'inactivetitletext' : 'inactive_title_text_color',
			'infotext' : 'tooltip_fg_color',
			'infowindow' : 'tooltip_bg_color',
			'menu' : 'menu_bg_color',
			'menutext' : 'menu_text_color',
			'scrollbar' : 'scrollbar_trough_bg_color',
			'titletext' : 'window_title_text_color',
			'window' : 'bg_bright',
			'windowframe' : False, 
			'windowtext' : ['fg_color', 'text_color'],
		}



		for color_name in self.theme_config['colors']:
			
			new_color = self.theme_config['colors'][color_name]['color']
			self.logger.info("{:<21} | New color: {}".format(color_name, new_color))
			for gtk_css in [ self.folder_names['theme']+"gtk-3.24/gtk.css", self.folder_names['theme']+"gtk-3.0/gtk.css"]:
				self.logger.debug("{:<21} | {} in {}".format(color_name, new_color, gtk_css))
				shutil.move( gtk_css, gtk_css+"~" )
				fileh = open(gtk_css+"~","r")
				nfileh = open(gtk_css,"w")
				for line in fileh:
					found = False
					if color_name in windows_to_gtk and windows_to_gtk[color_name]:
						if isinstance(windows_to_gtk[color_name], str):
							if " " + windows_to_gtk[color_name] + " " in line:
								self.logger.debug("{:<21} | FOUND! {} in {}".format("", windows_to_gtk[color_name],line.strip()))
								start = line.find(windows_to_gtk[color_name]) + len(windows_to_gtk[color_name]) + 1
								end = line.find(";", start)
								line = line.replace(line[start:end],new_color)
								self.logger.debug("{:<21} | Writting: {}".format("", line.strip()))
						else:
							for name in windows_to_gtk[color_name]:
								if " "+name in line:
									self.logger.debug("{:<21} | FOUND! {} in {}".format("", name, line.strip()))
									start = line.find(name) + len(name) + 1
									end = line.find(";", start)
									line = line.replace(line[start:end],new_color)
									self.logger.debug("{:<21} | Writting: {}".format("",line.strip()))
				
					nfileh.write(line)
				fileh.close()
				nfileh.close()

			#### THESE ARE LOCATED IN xfwm4/themerc
			# #activetitle
			#active_color_1=#000080
			#active_color_2=#000080

			#inactivetitle
			#inactive_color_1=#808080
			#inactive_color_2=#808080

			#activetext
			#active_text_color=#ffffff

			#inactivetext
			#inactive_text_color=#C0C0C0

			#buttonface
			#active_mid_1=#C0C0C0
			#inactive_mid_1=#C0C0C0

			#buttonLight
			#active_hilight_1=#DFDFDF
			#inactive_hilight_1=#DFDFDF

			#buttonhilight
			#active_hilight_2=#ffffff
			#inactive_hilight_2=#ffffff

			#activeborder
			#active_border_color=#C0C0C0
			#inactive_border_color=#C0C0C0

			#buttonShadow
			#active_shadow_2=#808080
			#inactive_shadow_2=#808080

			#buttonDKShadow
			#active_shadow_1=#000000
			#inactive_shadow_1=#000000

			#buttontext
			#active_mid_2=#000000
			#inactive_mid_2=#000000
			themerc_colors = {
				'activetitle' : ['active_color_1','active_color_2'],
				'inactivetitle' : ['inactive_color_1','inactive_color_2'],
				'titletext' : ['active_text_color'],
				'inactivetitletext' : ['inactive_text_color'],
				'buttonface' : ['active_mid_1','inactive_mid_1'],
				'buttonlight' : ['active_hilight_1','inactive_hilight_1'],
				'buttonhilight' : ['active_hilight_2','inactive_hilight_2'],
				'activeborder' : ['active_border_color'],
				'inactiveborder' : ['inactive_border_color'],
				'buttonshadow' : ['active_shadow_2','inactive_shadow_2'],
				'buttondkshadow' : ['active_shadow_1','inactive_shadow_1'],
				'buttontext' : ['active_mid_2','inactive_mid_2']
			}
			
			if color_name in themerc_colors:

				self.logger.debug("{:<21} | {}".format(color_name, themerc_colors[color_name]))
								
				for themerc in [ self.folder_names['theme']+'xfwm4/themerc', self.folder_names['theme']+'xfwm4_hidpi/themerc' ]:

					shutil.move( themerc, themerc+"~" )
					fileh = open(themerc+"~","r")
					nfileh = open(themerc,"w")
					for line in fileh:
						if line[0:line.find("=")] in themerc_colors[color_name]:
							self.logger.debug("{:<21} | Editing themerc color {} changing to {}".format('', color_name, new_color))
							line = line.replace(line[line.find("=")+1:],new_color+"\n")
						nfileh.write(line)
					fileh.close()
					nfileh.close()


		self.create_windows_controls(self.folder_names['theme'], 
						self.theme_config['colors']['buttondkshadow']['color'], 
						self.theme_config['colors']['buttonlight']['color'], 
						self.theme_config['colors']['buttonshadow']['color'], 
						self.theme_config['colors']['buttonhilight']['color'], 
						self.theme_config['colors']['buttonface']['color'], 
						self.theme_config['colors']['buttontext']['color'] )

		self.change_asset_colors(self.folder_names['theme'], 
						self.theme_config['colors']['buttondkshadow']['color'], 
						self.theme_config['colors']['buttonlight']['color'], 
						self.theme_config['colors']['buttonshadow']['color'], 
						self.theme_config['colors']['buttonhilight']['color'], 
						self.theme_config['colors']['buttonface']['color'], 
						self.theme_config['colors']['buttontext']['color'] )
		

		color_theme_config = configparser.RawConfigParser(interpolation=None)
		color_theme_config.optionxform = str
		color_theme_config.read(self.folder_names['theme']+"index.theme")
		color_theme_config.set("Desktop Entry","Name",self.index_theme_name)
		color_theme_config.set("X-GNOME-Metatheme","GtkTheme",self.index_theme_name)
		color_theme_config.set("X-GNOME-Metatheme","MetacityTheme",self.index_theme_name)
		color_theme_config.set("X-GNOME-Metatheme","IconTheme",self.index_theme_name)
		color_theme_config.set("X-GNOME-Metatheme","CursorTheme",self.index_theme_name)
		with open(self.folder_names['theme']+"index.theme", 'w') as configfile:
			color_theme_config.write(configfile,  space_around_delimiters=False)

	def find_all_wallpapers(self):
		# Finds all wallpapers included with the theme
		self.extra_wallpapers = []
		found = False
		self.logger.debug("Checking for any other wallpapers in theme folder")
		wallpaper_files = ('.bmp', '.gif', '.jpg', '.png', '.tif')
		for ext in wallpaper_files:
			for files in [self.theme_files[i] for i in self.theme_files if ext in i]:
				self.logger.debug("Extra wallpaper found: {} ".format(files))
				self.extra_wallpapers.append(files)
				found = True
		if not found:
			self.extra_wallpapers = False
		

	def generate_wallpaper(self):

		if not self.theme_config['wallpaper']['theme_wallpaper'] and not self.theme_config['wallpaper']['extra_wallpapers']:
			self.logger.info("No wallpapers included with this theme")
			return

		
		if (self.theme_config['wallpaper']['theme_wallpaper']['wallpaper']
			and self.theme_config['wallpaper']['theme_wallpaper']['path']):
			wallpaper = self.theme_config['wallpaper']['theme_wallpaper']['wallpaper']
			path = self.theme_config['wallpaper']['theme_wallpaper']['path']
			tilewallpaper = self.theme_config['wallpaper']['theme_wallpaper']['tilewallpaper']
			wallpaperstyle = self.theme_config['wallpaper']['theme_wallpaper']['wallpaperstyle']
			filename = self.theme_config['wallpaper']['theme_wallpaper']['new_filename']
			self.logger.info("Wallpaper:Wallpaper:Copying {} to {}".format(wallpaper,filename))
			self.logger.debug("Wallpaper: Copying {} to {}".format(path,self.folder_names['root']+filename))
			self.logger.debug("Wallpaper: {} path: {} tile: {} style: {} new_filename: {} root folder:{}".format(wallpaper, path, tilewallpaper, wallpaperstyle,filename, self.folder_names['root'] ))
			shutil.copy(path,self.folder_names['root']+filename)

		if self.theme_config['wallpaper']['extra_wallpapers']:
			for files in self.theme_config['wallpaper']['extra_wallpapers']:
				self.logger.info("Extra Wallpaper: Copying {} to {}".format(os.path.split(files)[-1],self.folder_names['root']))
				self.logger.debug("Extra Wallpaper: Copying {} to {}".format(files,self.folder_names['root']))
				shutil.copy(files,self.folder_names['root'])


					#shutil.copy(files,self.folder_names['root'])
	def generate_screensaver(self):
		self.logger.info("Generating screensaver")
		if self.theme_config['screensaver']: 
			self.logger.info("Copying {0} to {1}".format(self.theme_config['screensaver'], self.folder_names['screensaver']))
			shutil.copy(self.theme_config['screensaver'],self.folder_names['screensaver'])
			theme_screensaver = self.folder_names['screensaver'] + os.path.split(self.theme_config['screensaver'])[1]
			f = open(theme_screensaver[:-3]+"sh","w")
			f.write(SCREEN_SAVER_SCRIPT.format(scr_file=theme_screensaver))
			f.close()				
			

	def generate_fonts(self):
		self.logger.info("Copying fonts")
		for font in self.theme_config['fonts']:
			family = self.theme_config['fonts'][font]['family']
			path = self.theme_config['fonts'][font]['path']
			self.logger.info("Copying font {}: {} to {}".format(family, path, self.folder_names['fonts']+family+os.path.splitext(path)[1]))
			shutil.copy(path,self.folder_names['fonts']+family+os.path.splitext(path)[1])

	def generate_sounds(self):

		# Sound themes are like Icon theme. To disable a sound the .disable

		xdg_sounds_to_theme = { 
			'alarm-clock-elapsed' : 'SystemAsterisk',
			'audio-channel-front-center' : 'None',
			'audio-channel-front-left' : 'None',
			'audio-channel-front-right' : 'None',
			'audio-channel-left' : 'None',
			'audio-channel-lfe' : 'None',
			'audio-channel-rear-center' : 'None',
			'audio-channel-rear-left' : 'None',
			'audio-channel-rear-right' : 'None',
			'audio-channel-right' : 'None',
			'audio-channel-side-left' : 'None',
			'audio-channel-side-right' : 'None',
			'audio-test-signal' : 'SystemStart',
			'audio-volume-change' : 'Close',
			'battery-caution' : 'None',
			'battery-full' : 'None',
			'battery-low' : 'SystemExclamation',
			'bell-terminal' : 'SystemExclamation',
			'bell-window-system' : 'SystemExclamation',
			'button-pressed' : 'MenuCommand',
			'button-released' : 'None',
			'button-toggle-off' : 'MenuCommand',
			'button-toggle-on' : 'MenuCommand',
			'camera-focus' : 'None',
			'camera-shutter' : 'None',
			'complete-copy' : 'None',
			'complete-download' : 'None',
			'complete-media-burn' : 'None',
			'complete-media-burn-test' : 'None',
			'complete-media-format' : 'None',
			'complete-media-rip' : 'None',
			'complete-scan' : 'None',
			'completion-fail' : 'None',
			'completion-partial' : 'None',
			'completion-rotation' : 'None',
			'completion-sucess' : 'None',
			'count-down' : 'None',
			'desktop-login' : 'SystemStart',
			'desktop-logout' : 'SystemExit',
			'desktop-screen-lock' : 'None',
			'desktop-switch-left' : 'RestoreUp',
			'desktop-switch-right' : 'RestoreDown',
			'device-added' : 'None',
			'device-added-audio' : 'None',
			'device-added-media' : 'None',
			'device-removed' : 'None',
			'device-removed-audio' : 'None',
			'device-removed-media' : 'None',
			'dialog-cancel' : 'None',
			'dialog-error' : 'SystemExclamation',
			'dialog-information' : 'SystemAsterisk',
			'dialog-ok' : 'None',
			'dialog-question' : 'SystemQuestion',
			'dialog-warning' : 'SystemHand',
			'drag-accept' : 'None',
			'drag-fail' : 'None',
			'drag-start' : 'None',
			'expander-toggle-off' : 'RestoreDown',
			'expander-toggle-on' : 'RestoreUp',
			'file-trash' : 'EmptyRecycleBin',
			'item-deleted' : 'EmptyRecycleBin',
			'item-selected' : 'MenuCommand',
			'lid-close' : 'None',
			'lid-open' : 'None',
			'link-pressed' : 'None',
			'link-released' : 'None',
			'menu-click' : 'MenuCommand',
			'menu-popdown' : 'MenuPopup',
			'menu-popup' : 'MenuPopup',
			'menu-replace' : 'MenuPopup',
			'message-new-email' : 'None',
			'message-new-instant' : 'None',
			'message-sent-email' : 'None',
			'message-sent-instant' : 'None',
			'network-connectivity-error' : 'SystemExclamation',
			'network-connectivity-established' : 'None',
			'network-connectivity-lost' : 'SystemAsterisk',
			'notebook-tab-changed' : 'None',
			'phone-failure' : 'None',
			'phone-hangup' : 'None',
			'phone-incoming-call' : 'None',
			'phone-outgoing-busy' : 'None',
			'phone-outgoing-calling' : 'None',
			'power-plug' : 'None',
			'power-unplug' : 'None',
			'power-unplug-battery-low' : 'SystemExclamation',
			'screen-capture' : 'Open',
			'scroll-down' : 'None',
			'scroll-down-end' : 'None',
			'scroll-left' : 'None',
			'scroll-left-end' : 'None',
			'scroll-right' : 'None',
			'scroll-right-end' : 'None',
			'scroll-up' : 'None',
			'scroll-up-end' : 'None',
			'search-results' : 'None',
			'search-results-empty' : 'None',
			'service-login' : 'None',
			'service-logout' : 'None',
			'software-update-available' : 'SystemQuestion',
			'software-update-urgent' : 'AppGPFault',
			'suspend-error' : 'SystemExclamation',
			'suspend-resume' : 'None',
			'suspend-start' : 'None',
			'system-bootup' : 'None',
			'system-ready' : 'None',
			'system-shutdown' : 'None',
			'theme-demo' : 'SystemStart',
			'tooltip-popdown' : 'None',
			'tooltip-popup' : 'None',
			'trash-empty' : 'EmptyRecycleBin',
			'window-attention-active' : 'AppGPFault',
			'window-attention-inactive' : 'AppGPFault',
			'window-close' : 'Close',
			'window-inactive-click' : 'SystemAsterisk',
			'window-maximized' : 'Maximize',
			'window-minimized' : 'Minimize',
			'window-move-end' : 'None',
			'window-move-start' : 'None',
			'window-new' : 'Open',
			'window-resize-end' : 'None',
			'window-resize-start' : 'None',
			'window-slide-in' : 'None',
			'window-slide-out' : 'None',
			'window-switch' : 'None',
			'window-unmaximized' : 'Minimize',
			'window-unminimized' : 'Maximize'
		}		

		os.mkdir(self.folder_names['sounds'] + "stereo/")
		os.mkdir(self.folder_names['sounds'] + "theme_source/")

		for name in xdg_sounds_to_theme:
			if xdg_sounds_to_theme[name] in self.theme_config['sounds']:
				path = self.theme_config['sounds'][xdg_sounds_to_theme[name]]
				theme_file = self.folder_names['sounds'] + "stereo/" + name + ".wav" #it's gotta be wav
				self.logger.debug("Copying theme sound {}: {} to {}".format(xdg_sounds_to_theme[name], path, theme_file)) 
				if path:
					shutil.copy(path, theme_file)
			else:
				theme_file = self.folder_names['sounds'] + "stereo/" + name + ".disabled"
				#self.logger.debug("Copying theme sound {}: {} to {}".format(xdg_sounds_to_theme[name], path, theme_file)) 
				with open(theme_file, 'w') as fp: 
					pass

		for sound in self.theme_config['sounds']:
			path = self.theme_config['sounds'][sound]
			if path:
				self.logger.info("Copying sound {}: {} to {}".format(sound, path, self.folder_names['sounds']+"theme_source/"+sound+'_'+os.path.split(path)[1]))
				shutil.copy(path,self.folder_names['sounds']+"theme_source/"+sound+'_'+os.path.split(path)[1])
		
		config = configparser.ConfigParser()
		config.optionxform=str
		config.add_section('Sound Theme')
		config.set('Sound Theme', 'Name', self.theme_name)
		config.set('Sound Theme', 'Directories', 'stereo')
		config.add_section('stereo')
		config.set('stereo', 'OutputProfile', 'stereo')

		self.logger.debug("Writting sound config file {}".format(self.folder_names['sounds']+"index.theme"))
		with open(self.folder_names['sounds']+"index.theme", 'w') as configfile:
	        	config.write(configfile, space_around_delimiters=False)
			
		

#### Color Functions
	def hexToRGB(self, h):
		return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

	def rgbaToRGB(self, tup):
		return (tup[0],tup[1],tup[2])

	def create_windows_controls(self, path="./", ButtonDKShadow="#000000", ButtonLight="#dfdfdf", ButtonShadow="#808080", ButtonHilight="#ffffff", ButtonFace="#c0c0c0", ButtonText="#FFFF00" ):
	
		convert_path = subprocess.check_output(["which", "convert"]).strip()
		mogrify_path = subprocess.check_output(["which", "mogrify"]).strip()
		# convert -size 18x18 xc:none 
		# -fill "#000000" -draw "rectangle 1,1 16,14" 
		# -fill "#ffffff" -draw "rectangle 1,1 15,13" 
		# -fill "#808080" -draw "rectangle 2,2 15,13" 
		# -fill "#dfdfdf" -draw "rectangle 2,2 14,12" 
		# -fill "#c0c0c0" -draw "rectangle 3,3 14,12" 
		# /home/phil/Chicago95/Theme/Chicago95/gtk-3.0/buttons/icon-restore.png -geometry +4+2 -composite 
		# test1.png

		size="18x18"
				
		self.logger.debug("{:<21} | Colors: ButtonDKShadow={}, ButtonLight={}, ButtonShadow={}, ButtonHilight={}, ButtonFace={}, ButtonText={} ".format("Colors",ButtonDKShadow, ButtonLight, ButtonShadow, ButtonHilight, ButtonFace, ButtonText))

		for i in ['gtk-3.0/']:
			
			folder = path + i + "buttons/"

			icons = {
			'close' : folder+"icon-close.png",
			'maximize' : folder+"icon-maximise.png",
			'minimize' : folder+"icon-minimise.png",
			'restore' : folder+"icon-restore.png"
			}

			
			# Windows control / title icons
			for icon in icons:
				
				filename = icon+"_normal.png"
				geometry="+3+2"

				if icon == 'close':
					geometry="+4+2"
				
				
				self.logger.debug("{:<21} | {}".format(icon, folder+filename))
				args = [
				convert_path,
				"-size", size,
				"xc:none",
				"-fill", ButtonDKShadow,
				"-draw", " rectangle 1,1 16,14", 
				"-fill", ButtonHilight,
				"-draw", " rectangle 1,1 15,13", 
				"-fill", ButtonShadow,
				"-draw", " rectangle 2,2 15,13", 
				"-fill", ButtonLight,
				"-draw", "rectangle 2,2 14,12", 
				"-fill", ButtonFace,
				"-draw", "rectangle 3,3 14,12", 
				"(", icons[icon], '-fill', ButtonText, '-opaque', '#000000', ")",
				'-geometry', geometry,
				'-composite',
				folder+filename
				]
				subprocess.check_call(args)

				filename = icon+"_pressed.png"
				
				geometry="+4+3"
				if icon == 'close':
					geometry="+5+3"
	
				self.logger.debug("{:<21} | {}".format(icon, folder+filename))
				args = [
				convert_path,
				"-size", size,
				"xc:none",
				"-fill", ButtonHilight,
				"-draw", " rectangle 1,1 16,14", 
				"-fill", ButtonDKShadow,
				"-draw", " rectangle 1,1 15,13", 
				"-fill", ButtonLight,
				"-draw", " rectangle 2,2 15,13", 
				"-fill", ButtonShadow,
				"-draw", "rectangle 2,2 14,12", 
				"-fill", ButtonFace,
				"-draw", "rectangle 3,3 14,12", 
				"(", icons[icon], '-fill', ButtonText, '-opaque', '#000000', ")",
				'-geometry', geometry,
				'-composite',
				folder+filename
				]
				subprocess.check_call(args)
				
				self.logger.debug("{:<21} | {}".format(icon, icons[icon]))
				args = [
				mogrify_path,
				'-fill', ButtonText, '-opaque', '#000000',
				icons[icon]
				]
				subprocess.check_call(args)
			

			self.logger.debug("{:<21} | {}".format("dialog_button_normal", folder+"dialog_button_normal.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonHilight,
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonLight,
			"-draw", "rectangle 1,1 13,13", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 13,13", 
			folder+"dialog_button_normal.png",
				]
			subprocess.check_call(args)
			
			self.logger.debug("{:<21} | {}".format("button_pressed", folder+"button_pressed.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonHilight,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 14,14", 
			folder+"button_pressed.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("combobox_button_normal", folder+"combobox_button_normal.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonFace, #ButtonHilight,
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonHilight,
			"-draw", "rectangle 1,1 13,13", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 13,13", 
			folder+"combobox_button_normal.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("decoration_border", folder+"decoration_border.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonLight, 
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonHilight,
			"-draw", "rectangle 1,1 13,13", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 13,13", 
			folder+"decoration_border.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("dialog_button_active", folder+"dialog_button_active.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonShadow, 
			"-draw", " rectangle 1,1 14,14",  
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 13,13", 
			folder+"dialog_button_active.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("dialog_button_focus", folder+"dialog_button_focus.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonHilight,
			"-draw", " rectangle 1,1 13,13", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 2,2 13,13", 
			"-fill", ButtonLight,
			"-draw", "rectangle 2,2 12,13", 
			"-fill", ButtonFace,
			"-draw", "rectangle 3,3 12,13", 
			folder+"dialog_button_focus.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("toggle_pressed", folder+"toggle_pressed.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonHilight,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonLight,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonShadow,
			"-draw", "rectangle 1,1 13,13", 
			"-fill", ButtonHilight,
			"-draw", "rectangle 2,2 13,12", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,3 13,13", 
			folder+"toggle_pressed.png",
				]
			subprocess.check_call(args)

			self.logger.debug("{:<21} | {}".format("decoration_border", folder+"decoration_border.png"))
			args = [
			convert_path,
			"-size", "16x16",
			"xc:none",
			"-fill", ButtonDKShadow,
			"-draw", " rectangle 0,0 15,15", 
			"-fill", ButtonHilight,
			"-draw", " rectangle 0,0 14,14", 
			"-fill", ButtonShadow,
			"-draw", " rectangle 1,1 14,14", 
			"-fill", ButtonHilight,
			"-draw", "rectangle 1,1 13,13", 
			"-fill", ButtonFace,
			"-draw", "rectangle 2,2 13,13", 
			folder+"decoration_border.png",
				]
			subprocess.check_call(args)

	def change_asset_colors(self, path="./", ButtonDKShadow="#000000", ButtonLight="#dfdfdf", ButtonShadow="#808080", ButtonHilight="#ffffff", ButtonFace="#c0c0c0", ButtonText="#000000" ):

		mogrify_path = subprocess.check_output(["which", "mogrify"]).strip()

		self.logger.debug("{:<21} | Colors: ButtonDKShadow={}, ButtonLight={}, ButtonShadow={}, ButtonHilight={}, ButtonFace={}, ButtonText={} ".format("Colors",ButtonDKShadow, ButtonLight, ButtonShadow, ButtonHilight, ButtonFace, ButtonText))

		originals = {
			'ButtonDKShadow' :"#000000",
			'ButtonLight' : "#dfdfdf",
			'ButtonShadow': "#808080", 
			'ButtonHilight' : "#ffffff", 
			'ButtonFace' : "#c0c0c0", 
			'ButtonText' : "#FFFF00"
		}

		new = {
			'ButtonDKShadow' : ButtonDKShadow,
			'ButtonLight' : ButtonLight,
			'ButtonShadow': ButtonShadow, 
			'ButtonHilight' : ButtonHilight, 
			'ButtonFace' : ButtonFace, 
			'ButtonText' : ButtonText
		}


		for i in ['gtk-3.0/assets/', 'gtk-3.24/assets/', 'gtk-3.0/scrollbar/', 'gtk-3.24/scrollbar/']:
			folder = path + i
			for asset in os.listdir(folder):
				asset_path = os.path.join(folder, asset)  # Get full path of the asset

				# If the asset is a directory, iterate over its contents
				if os.path.isdir(asset_path):
					self.logger.info(f"Entering directory: {asset_path}")
					for sub_asset in os.listdir(asset_path):
						sub_asset_path = os.path.join(asset_path, sub_asset)
						if os.path.isfile(sub_asset_path):  # Ensure it's a valid file
							self.logger.debug(
								f"mogrifying {sub_asset} in {asset_path} "
								f"({ButtonDKShadow}, {ButtonLight}, {ButtonShadow}, "
								f"{ButtonHilight}, {ButtonFace}, {ButtonText})"
							)
							args = [
								mogrify_path,
								'-fill', ButtonDKShadow, '-opaque', originals['ButtonDKShadow'],
								'-fill', ButtonLight, '-opaque', originals['ButtonLight'],
								'-fill', ButtonShadow, '-opaque', originals['ButtonShadow'],
								'-fill', ButtonHilight, '-opaque', originals['ButtonHilight'],
								'-fill', ButtonFace, '-opaque', originals['ButtonFace'],
								'-fill', ButtonText, '-opaque', originals['ButtonText'],
								'-quiet',
								sub_asset_path
							]

							try:
								subprocess.check_call(args)
							except subprocess.CalledProcessError as e:
								self.logger.error(f"Failed to process file {sub_asset_path}: {e}")
						else:
							self.logger.warning(f"Skipping non-file in directory: {sub_asset_path}")
					continue  # Skip further processing of the directory itself

				# Process regular files in the current folder
				if not asset.startswith("status") and not asset.startswith("branding"):
					self.logger.debug(
						f"mogrifying {asset} ({ButtonDKShadow}, {ButtonLight}, {ButtonShadow}, "
						f"{ButtonHilight}, {ButtonFace}, {ButtonText})"
					)
					args = [
						mogrify_path,
						'-fill', ButtonDKShadow, '-opaque', originals['ButtonDKShadow'],
						'-fill', ButtonLight, '-opaque', originals['ButtonLight'],
						'-fill', ButtonShadow, '-opaque', originals['ButtonShadow'],
						'-fill', ButtonHilight, '-opaque', originals['ButtonHilight'],
						'-fill', ButtonFace, '-opaque', originals['ButtonFace'],
						'-fill', ButtonText, '-opaque', originals['ButtonText'],
						'-quiet',
						asset_path
					]

					try:
						subprocess.check_call(args)
					except subprocess.CalledProcessError as e:
						self.logger.error(f"Failed to process file {asset_path}: {e}")
			

#### Icon/Cursor Functions

	def get_icons_size_ico(self, icons_list, size=32):
		self.logger.debug("{:<21} | Getting highest quality icon of size {}".format(" ",size)) 
		
		size_exists = False
		highest_color = 0
		
		for icon_data in icons_list: # First we make sure the ID exists and get the highest rating

			if int(icon_data['Width']) == int(size):
				size_exists = True
			
				if icon_data['Colors'] >= highest_color: 
					highest_color = icon_data['Colors']

		
		#Return that Icon file
		if size_exists:
			for i in icons_list:
				if "_{}x{}x{}.ico".format(size, size,highest_color) in i['filename']:
					self.logger.debug("{:<21} | Found: {}".format("", i['filename']))
					return i['filename'], i['ICON'] 

		else:
			self.logger.debug("{:<21} | Could not find Icon of size {}".format(" ", size))
			return (False,False)

		self.logger.debug("{:<21} | Could not find Icon of size {}".format(" ", size))
		return (False,False)



	def get_icons_size_dll(self, icons_list, index, size=32):
		self.logger.debug("{:<21} | Getting highest quality icon of size {} at index {}".format(" ", size, index)) 
		
		id_exists = False
		size_exists = False
		highest_color = 0
		
		for icon_data in icons_list: # First we make sure the ID exists and get the highest rating

			if int(icon_data['ID']) == int(index) and int(icon_data['Width']) == int(size):
				id_exists = True
				size_exists = True

				if icon_data['Colors'] >= highest_color: highest_color = icon_data['Colors']

		
		#Return that Icon file
		if id_exists and size_exists:
			for i in icons_list:
				if "{}_{}x{}x{}.ico".format(index, size, size,highest_color) in i['filename']:
					self.logger.debug("{:<21} | CFound: {}".format("",i['filename']))
					return i['filename'], i['ICON'] 
		else:
			self.logger.debug("{:<21} | Could not find Icon with index {}".format(" ",index))
			return (False,False)



	def get_largest_icon_dll(self, icons_list, index):
		self.logger.debug("{:<21} | Getting highest quality icon at index {}".format(" ",index)) 
		
		highest_color = 0
		highest_size = 0
		id_exists = False
		
		for icon_data in icons_list: # Find the highest quality icon
			if int(icon_data['ID']) == int(index):
				id_exists = True
				if icon_data['Colors'] >= highest_color: highest_color = icon_data['Colors']
				if icon_data['Width'] >= highest_size: highest_size = icon_data['Width']
		
		#Return that Icon file
		if id_exists:
			for i in icons_list:
				if "{}_{}x{}x{}.ico".format(index, highest_size, highest_size,highest_color) in i['filename']:
					self.logger.debug("{:21} | Found: {}".format("", i['filename']))
					return i['filename'], i['ICON'] 
		else:
			self.logger.error("{:21} | Could not find Icon with index {}".format("",index))
			return ('','')

	def get_largest_icon_ico(self, icons_list, index):
		self.logger.debug("{:<21} | Getting highest quality icon".format(" ")) 
		
		highest_color = 0
		highest_size = 0
		size_exists = False		
		for icon_data in icons_list: # Find the highest quality icon
			if icon_data['Colors'] >= highest_color: highest_color = icon_data['Colors']
			if icon_data['Width'] >= highest_size: highest_size = icon_data['Width']
		
		#Return that Icon file
		
		for i in icons_list:
			if "{}x{}x{}.ico".format(highest_size, highest_size,highest_color) in i['filename']:
				self.logger.debug("{:21} | Found: {}".format("", i['filename']))
				return i['filename'], i['ICON'] 
		else:
			self.logger.error("{:<21} | Could not find Icon with index {}".format(" ", index))
			return ('','')
				
				
	def extract_icons_from_dll(self, dll_file_path, dump=False, folder="./"):
		# This function extracts icons from DLL files (and ICL files)
		# Returns a list of dicts with the file name containing the name, index, width, height, colors and the icon itself
		# This is kludgy as hell but it works

		# Mostly built off of:
		# https://www.codeproject.com/Articles/16178/IconLib-Icons-Unfolded-MultiIcon-and-Windows-Vista
		# https://hwiegman.home.xs4all.nl/fileformats/exe/WINHDR.TXT

		group_type = { 3: 'RT_ICON', 14 :'RT_GROUP_ICON' }
		ICONS = []

		if not dll_file_path:
			return False

		f = open(dll_file_path,'rb')
		dll_file = f.read()
		f.close()
		dll_bytes = bytearray(dll_file)
		
		self.logger.debug("{:<21} | Parsing DLL file {} with: dump={}, folder={}".format('',dll_file_path, dump, folder)) 
		self.logger.debug("{:<21} | Parsing NE DLL/ICL".format(''))
		e_lfanew =  struct.unpack('<I',dll_bytes[60:64])[0]
		ne_header_char = dll_bytes[e_lfanew:e_lfanew+2].decode()

		if ne_header_char == 'NE':
			self.logger.debug("{:<21} | NE Header: {}".format('', ne_header_char))

			ne_rsrctab = struct.unpack('<H',dll_bytes[e_lfanew+36:e_lfanew+36+2] )[0] + e_lfanew
			rscAlignShift = struct.unpack('<H',dll_bytes[ne_rsrctab:ne_rsrctab+2] )[0]
			resource_table = {'rscAlignShift':rscAlignShift, 'rscTypes': [], 'rscEndTypes' : 0, 'rscResourceNames': [], 'rscEndNames': 0}

			self.logger.debug("{:<21} | Offset from 0 to NE header (e_lfanew): {}".format('',e_lfanew))
			self.logger.debug("{:<21} | Parsing Resource Tables (ne_rsrctab) at {} ({})".format('',ne_rsrctab, hex(ne_rsrctab)))

			TNAMEINFO = []
			ptr = ne_rsrctab+2 #Advance ptr to TYPEINFO
			rttypeid = 1
			while rttypeid != 0 and rttypeid < 24:
				tmp_ba = dll_bytes[ptr:]
				rttypeid = struct.unpack('<H',tmp_ba[0:2] )[0] & 0x7FFF
				if rttypeid == 0 or rttypeid > 24: 
					continue # At the end of the type info array exit
				rtresourcecount = struct.unpack('<H',tmp_ba[2:4] )[0]
				tmp_ba = dll_bytes[ptr+8:]
				self.logger.debug("{:<21} | Type ID {} has {} records".format('',group_type[rttypeid], rtresourcecount, ptr+8, hex(ptr+8)))

				size = 0
				for x in range(0, rtresourcecount):

					TNAMEINFO.append( {
					'rttypeid' : rttypeid,
					'rnOffset' : struct.unpack('<H',tmp_ba[size+ 0:size+2])[0] << rscAlignShift,
					'rnLength' : struct.unpack('<H',tmp_ba[size+ 2:size+4])[0],
					'rnFlags'  : struct.unpack('<H',tmp_ba[size+ 4:size+6])[0],
					'rnID'     : struct.unpack('<H',tmp_ba[size+ 6:size+8])[0] & 0x7FFF,
					'rnHandle' : struct.unpack('<H',tmp_ba[size+ 8:size+10])[0],
					'rnUsage'  : struct.unpack('<H',tmp_ba[size+ 10:size+12])[0]
					} )
					
					size = size + 12 #Skip ahead these entries
				ptr = ptr + size + 8 # Skip to the next TYPEINFO

			ptr = ptr + 2 # rscEndTypes
			tmp_ba = dll_bytes[ptr:]
			names = 0
			length = 1
			#Resource Names
			RESOURCENAMES = []

			while length != 0:
				length = tmp_ba[names]
				RESOURCENAMES.append(tmp_ba[names+1:names+1+length].decode())
				names = names + tmp_ba[names] + 1
			
			resource_table['rscResourceNames'].extend(RESOURCENAMES)
			resource_table['rscTypes'].extend(TNAMEINFO)

			for GRPICONDIRENTRY in resource_table['rscTypes']:
				if GRPICONDIRENTRY['rttypeid'] == 14: #RT_GROUP_ICON	
					try:
						name = RESOURCENAMES[GRPICONDIRENTRY['rnID']]
					except (KeyError, IndexError):
						name = os.path.splitext(dll_file_path.split("/")[-1])[0]
						pass
					idReserved = struct.unpack('<H',dll_bytes[GRPICONDIRENTRY['rnOffset']+0:GRPICONDIRENTRY['rnOffset']+2])[0]
					idType = struct.unpack('<H',dll_bytes[GRPICONDIRENTRY['rnOffset']+2:GRPICONDIRENTRY['rnOffset']+4])[0]
					idCount = struct.unpack('<H',dll_bytes[GRPICONDIRENTRY['rnOffset']+4:GRPICONDIRENTRY['rnOffset']+6])[0]
					tmp_grp = dll_bytes[GRPICONDIRENTRY['rnOffset']+6:]
					for x in range(0, idCount):
						rtIcon = {
						'bWidth'       : tmp_grp[0], # Width, in pixels, of the image
						'bHeight'      : tmp_grp[1], # Height, in pixels, of the image
						'bColorCount'  : tmp_grp[2], # Number of colors in image (0 if >=8bpp)
						'bReserved'    : tmp_grp[3], # Reserved
						'wPlanes'      : struct.unpack('<H',tmp_grp[4:6])[0], # Color Planes
						'wBitCount'    : struct.unpack('<H',tmp_grp[6:8])[0], # Bits per pixel
						'dwBytesInRes' : struct.unpack('<L',tmp_grp[8:12])[0], # how many bytes in this resource?
						'nId'          : struct.unpack('<H',tmp_grp[12:14])[0] # RT_ICON rnID
						}
						
						for RT_ICON in resource_table['rscTypes']:
							if RT_ICON['rttypeid'] == 3 and  RT_ICON['rnID'] == rtIcon['nId']:
								icon_file = bytearray(2) + struct.pack('<H',1) + struct.pack('<H',1)
								ICONENTRY = tmp_grp[0:12] + struct.pack('<L', 22)
								icon_bitmap = dll_bytes[RT_ICON['rnOffset']:RT_ICON['rnOffset']+rtIcon['dwBytesInRes']]
								#print(ICONENTRY)
								if rtIcon['bColorCount'] == 0: rtIcon['bColorCount'] = 256
								filename = "{}_{}_{}x{}x{}.ico".format(name, GRPICONDIRENTRY['rnID'], rtIcon['bWidth'], rtIcon['bHeight'], rtIcon['bColorCount'])

								if dump:
									self.logger.info("{:<21} | Creating: {}".format('', folder + filename))
									f = open(folder + filename,"wb")
									f.write(icon_file+ICONENTRY+icon_bitmap)
									f.close()
								ICONS.append({
									'filename': filename, 
									'ID'      : GRPICONDIRENTRY['rnID'],
									'Width'   : rtIcon['bWidth'],
									'Height'  : rtIcon['bHeight'],
									'Colors'  : rtIcon['bColorCount'],
									'ICON': icon_file+ICONENTRY+icon_bitmap})
						tmp_grp = tmp_grp[14:]
		
		return ICONS
	
	def extract_cur(self, file_name):
		self.logger.debug("{:21} | Parsing cursor file {}".format("", file_name)) 
		# input: .cur file location/name
		# output: dict with cursor information

		f = open(file_name,'rb')
		cur_file = f.read()
		f.close()
		cur_bytes = bytearray(cur_file)
		rtIconDir = False
		rtIconDirEntry = False
		INFO = False
		icon = []
		
		icon.append({
			'rtIconDir' : {
			'res' : struct.unpack('<H',cur_bytes[0:2])[0],
			'ico_type' : struct.unpack('<H',cur_bytes[2:4])[0],
			'ico_num_images' : struct.unpack('<H',cur_bytes[4:6])[0]
			},
			'ico_file' : cur_bytes,
			#ICONDIRENTRY
			# TODO Add multiple cursors here if needed like icons
			'rtIconDirEntry' : {
				'bWidth'       : cur_bytes[6], # Width, in pixels, of the image
				'bHeight'      : cur_bytes[7], # Height, in pixels, of the image
				'bColorCount'  : cur_bytes[8], # Number of colors in image (0 if >=8bpp)
				'bReserved'    : cur_bytes[9], # Reserved
				'wPlanes'      : struct.unpack('<H',cur_bytes[10:12])[0], # Color Planes
				'wBitCount'    : struct.unpack('<H',cur_bytes[12:14])[0], # Bits per pixel
				'dwBytesInRes' : struct.unpack('<L',cur_bytes[14:18])[0], # how many bytes in this resource?
				'dwDIBOffset'  : struct.unpack('<H',cur_bytes[18:20])[0] # RT_ICON rnID
			}
			
		})

		cursor = {
			'icon' : icon 
		}

		return cursor

	def extract_ico(self, file_name, dump=False, folder='./'):
		self.logger.debug("{:21} | Parsing ICO file {} with: dump={}, folder={}".format("", file_name, dump, folder)) 

		if not file_name:
			self.logger.error("ICO file does not exist. Enable debug for more information")
			return False
		# input: .ico file location/name
		# output: dict with icon information

		f = open(file_name,'rb')
		cur_file = f.read()
		f.close()
		cur_bytes = bytearray(cur_file)

		if cur_bytes[0:2].decode() == "BM":
			return "bmp"

		rtIconDir = False
		rtIconDirEntry = False
		ICONS = []
		
		idReserved = struct.unpack('<H',cur_bytes[0:2])[0]
		idType = struct.unpack('<H',cur_bytes[2:4])[0]
		idCount = struct.unpack('<H',cur_bytes[4:6])[0]
		loc = 6
		if idType == 1: # ICONS ONLY NO CURSORS
			name = os.path.splitext(os.path.basename(file_name))[0]
			for i in range(0,idCount):
				
				#ICONDIRENTRY

				rtIconDirEntry = {
					'bWidth'       : cur_bytes[loc], # Width, in pixels, of the image
					'bHeight'      : cur_bytes[loc+1], # Height, in pixels, of the image
					'bColorCount'  : cur_bytes[loc+2], # Number of colors in image (0 if >=8bpp)
					'bReserved'    : cur_bytes[loc+3], # Reserved
					'wPlanes'      : struct.unpack('<H',cur_bytes[loc+4:loc+6])[0], # Color Planes
					'wBitCount'    : struct.unpack('<H',cur_bytes[loc+6:loc+8])[0], # Bits per pixel
					'dwBytesInRes' : struct.unpack('<L',cur_bytes[loc+8:loc+12])[0], # how many bytes in this resource?
					'dwImageOffset'  : struct.unpack('<L',cur_bytes[loc+12:loc+16])[0] # RT_ICON rnID
				}
				
				
				ICONHEADER = bytearray(2) + struct.pack('<H',1) + struct.pack('<H',1)
				IconDirectoryEntry = cur_bytes[loc:loc+12] + struct.pack('<L', 22)
				img = cur_bytes[rtIconDirEntry['dwImageOffset']:rtIconDirEntry['dwImageOffset']+rtIconDirEntry['dwBytesInRes']]

				if rtIconDirEntry['bColorCount'] == 0: rtIconDirEntry['bColorCount'] = 256

				filename = "{}_{}_{}x{}x{}.ico".format(name, i, rtIconDirEntry['bWidth'], rtIconDirEntry['bHeight'], rtIconDirEntry['bColorCount'])

				if dump:
					self.logger.info("Creating:", folder + filename)
					f = open(folder + filename,"wb")
					f.write(ICONHEADER+IconDirectoryEntry+img)
					f.close()
				ICONS.append({
					'filename': filename, 
					'ID'      : i,
					'Width'   : rtIconDirEntry['bWidth'],
					'Height'  : rtIconDirEntry['bHeight'],
					'Colors'  : rtIconDirEntry['bColorCount'],
					'ICON': ICONHEADER+IconDirectoryEntry+img
				})

				loc += 16

		return ICONS			

	def extract_ani(self, file_name):
		# convert an ani a dict with Icon information
		# input: .ani file location/name
		# output: dict with cursor information

		# from http://www.toolsandtips.de/Tutorial/Aufbau-Animierte-Cursor.htm
		#1. 0000. First RIFF : then the size of the file as DWORD, a total of 8 bytes.  Note the length of the file can be different!  
		#	A: the actual length of the file.  
		#	B: the length of the file minus the 8 bytes for RIFF and the DWORD for the length specification.  
		#2. 0008. ACON : This part may contain the following.  Optional!  
		#	LIST : Length as DWORD to "anih" without the 4 bytes of the length specification from LIST .  The data can be: Optional!  
		#		INAM: Size of the title as DWORD without the 4 bytes of the length specification, then data.  Note there can be "INFO" in front of it!  Optional!  
		#	IART: Length from the author as DWORD without the 4 bytes of the length specification, then data.  
		#	anih : size of the Ani header structure as DWORD maximum 36 bytes, then the structure with 36 bytes.  The first value of the DWORD is with the size of the structure = 36 bytes.  (See Ani header structure).  
		#	rate : size of the rate as DWORD.  Data in DWORDs.  The specification of "rate" can also be optional !  
		#		With which the speed of the image change can be adjusted more finely, does not have to be.  
		#		Since a standard value for the speed is already entered in the Ani header structure (ANIHEADER.iDispRate) !  
		#		According to the length specification.  So with Hex 10 = 16 bytes, 4 DWORDs = 16 bytes follow.  
		#		Example: The Ani has 4 pictures, then a " DWORD " followed by a DWORD with a hex number 10 = 16 bytes, the length as DWORD! 
		#		This DWORD is followed by a DWORD for each picture, which indicates the speed of the picture change.  That can be different.  
		#		Eg.  For 4 pictures 0000 0011, 0000 0011, 0000 0011, 0000 0011.or: for 4 pictures 0000 0011, 0000 0030, 0000 0050, 0000 0018.
		#	seq : Size of the sequence block as DWORD, data in DWORDs.  The specification of "seq" can also be optional !  
		#		What the order of the images is in the animation before the animation is repeated.  
		#		Eg.  5 pictures are actually in the file (ANIHEADER.nFrames = 5) in ANIHEADER.nSteps = 8 there are 8 pictures.  
		#		The length of "seq" would then be Hex 20 = 32 bytes = 8 DWORD.  
		#		The arrangement of the pictures could be picture 1, picture 1, picture 2, picture 3, picture 4, picture 1, picture 2, picture 5 then the series is repeated.  
		#		If the order of the pictures were 1,2,3,4,5, then you don't actually need a "seq" block.  
		#		If there are more pictures in the ANIHEADER.nSteps than in the ANIHEADER.nFrames then the "seq" block is mandatory!  
		#		Which of course must then correspond to the size of the number of images, e.g. 8 images * 4 bytes (= 1DWORD) = 32 bytes = hex 20 = 8 DWORDs.  
		#		Furthermore, if the "rate" block is to be used, the "rate" block must have the same size as the "seq" block, ie also 32 bytes = 8 DWORDs!  One DWORD for each image to be displayed.  
		#
		# 3. LIST : Length of the rest of the file, as DWORD, from this length specification, that is after this DWORD.  
		#	fram: 
		#		icon : Size of the image data after this DWORD, then data.  (First picture) 
		#		Note!  In the size specification, the sizes of the two cursor structures, the BITMAPINFOHEADER structure, the color table and the XOR and the AND image are added together.  
		#		So from here to the next "icon" frame, or the end of the file if it is the last picture.  The icon block contains according to the size specification.  
		#			A: The structure CURHEADER (or iconheader) with the size is 6 bytes.  (see CURHEADER structure).  
		#			B: The structure CURSORDIEENTRY (or icondir) with the size is 16 bytes.  (see CURSORDIEENTRYR structure) 
		#			C: the structure BITMAPINFOHEADER with the size is 40 bytes.  (see BITMAPINFOHEADER structure) 
		#			D: color table (number of colors * 4 bytes) 
		#			E: image data of the cursor first the XOR image then the AND image ........ ........ (etc.) . ....... 
		#
		#		icon : size of the image data after this DWORD, then data.  (Last picture) 
		#		Note!  In the size specification, the sizes of the two cursor structures, the BITMAPINFOHEADER structure, the color table and the XOR and the AND image are added together.  
		#		So from here to the end of the file.  The icon block contains according to the size specification.  
		#			A: The structure CURHEADER with the size is 6 bytes.  (see CURHEADER structure) 
		#			B: the structure CURSORDIEENTRY with the size is 16 bytes.  (see CURSORDIEENTRYR structure) 
		#			C: the structure BITMAPINFOHEADER with the size is 40 bytes.  (see BITMAPINFOHEADER structure) 
		#			D: color table (number of colors * 4 bytes) 
		#			E: image data of the cursor first the XOR image then the AND image 
		#

		f = open(file_name,'rb')
		ani_file = f.read()
		f.close()
		ani_bytes = bytearray(ani_file)

		rate = False
		seq = False
		rtIconDir = False
		rtIconDirEntry = False
		INFO = False
		anih = False
		icon = []
		icon_count = 0
		
		ckID   = ani_bytes[0:4].decode()
		ckSize =  struct.unpack('<L',ani_bytes[4:8])[0]
		ckForm = ani_bytes[8:12].decode()

		total_size = 0
		self.logger.debug("{:<21} | Extracting cursors/icons from ani file: {}".format("", file_name))

		# ANI files are just RIFF files
		if ckID == 'RIFF':
			self.logger.debug("{:<21} | {} ckSize :{}".format("","RIFF detected", ckSize))
			if ckForm == 'ACON': #ACON is optional
				#self.logger.debug("ACON detected (optional)")
				total_size = 12 # RIFF Header with ACON
			else:
				total_size = 8 # RIFF Header without ACON

			if ckSize == len(ani_bytes) - 8:
				ckSize = ckSize + 8 # Sometimes, but not always, the header isn't included in ckSize
				self.logger.debug("{:<21} | Adjusting ckSize to actual file size: {}".format("",ckSize))

			while total_size < ckSize:
				section = ani_bytes[total_size:total_size+4].decode()
				total_size = total_size + 4
				chunk_size = struct.unpack('<L',ani_bytes[total_size:total_size+4])[0]
				total_size = total_size + 4

				#print("Chunk {}, Size: {}".format(section, chunk_size))
				#print(ani_bytes[total_size:total_size+36])
				if section == 'anih': #ANI Header
					self.logger.debug("{:<21} | Chunk: anih".format(""))
					anih = {
						'cbSize': struct.unpack('<L',ani_bytes[total_size:total_size+4])[0],
						'nFrames': struct.unpack('<L',ani_bytes[total_size+4:total_size+8])[0],
						'nSteps' : struct.unpack('<L',ani_bytes[total_size+8:total_size+12])[0],
						'iWidth' : struct.unpack('<L',ani_bytes[total_size+12:total_size+16])[0],
						'iHeight' : struct.unpack('<L',ani_bytes[total_size+16:total_size+20])[0],
						'iBitCount' : struct.unpack('<L',ani_bytes[total_size+20:total_size+24])[0],
						'nPlanes' : struct.unpack('<L',ani_bytes[total_size+24:total_size+28])[0],
						'iDispRate' : struct.unpack('<L',ani_bytes[total_size+28:total_size+32])[0], # The value is expressed in 1/60th-of-a-second units, which are known as jiffie, ignored if seq exists
						'bfAttributes' : struct.unpack('<L',ani_bytes[total_size+32:total_size+36])[0]
					}
				elif section == 'rate':
					self.logger.debug("{:<21} | Chunk: rate, size: {}".format("", chunk_size))
					rate = []
					for jiffie in range(0,chunk_size,4):
						rate.append(struct.unpack('<L',ani_bytes[total_size+jiffie:total_size+jiffie+4])[0])
				elif section == 'seq ':
					self.logger.debug("{:<21} | Chunk: seq, size: {}".format("",chunk_size))
					seq = []
					for sequence in range(0,chunk_size,4):
						seq.append(struct.unpack('<L',ani_bytes[total_size+sequence:total_size+sequence+4])[0])
					# bfAttributes: 1 == CUR or ICO, 0 == BMP, 3 == 'seq' block is present
				elif section == 'LIST':
					chunk_type = ani_bytes[total_size:total_size+4].decode()
					LIST_item_size = total_size + 4
					self.logger.debug("{:<21} | Chunk: {}, size: {}".format("",chunk_type, chunk_size))
					if chunk_type == 'INFO':
						INFO = {}
						while LIST_item_size <= chunk_size:
							try:					
								info_section = ani_bytes[LIST_item_size:LIST_item_size+4].decode()
								list_chunk_size = struct.unpack('<L',ani_bytes[LIST_item_size+4:LIST_item_size+8])[0]
								INFO[info_section] = ani_bytes[LIST_item_size+8:LIST_item_size+8+list_chunk_size].decode()
							except UnicodeDecodeError:					
								info_section = ani_bytes[LIST_item_size:LIST_item_size+4].decode('latin-1')
								list_chunk_size = struct.unpack('<L',ani_bytes[LIST_item_size+4:LIST_item_size+8])[0]
								INFO[info_section] = ani_bytes[LIST_item_size+8:LIST_item_size+8+list_chunk_size].decode('latin-1')
							
				
							if (list_chunk_size % 2) != 0: # Yay DWORD boundaries
								list_chunk_size = list_chunk_size + 1
							LIST_item_size = LIST_item_size + list_chunk_size + 8
					elif chunk_type == 'fram':
						info_section = ani_bytes[LIST_item_size:LIST_item_size+4].decode()
						while LIST_item_size < chunk_size:
							self.logger.debug("{:<21} | Chunk: {}, size: {}".format("",info_section, LIST_item_size))
							info_section = ani_bytes[LIST_item_size:LIST_item_size+4].decode()
							list_chunk_size = struct.unpack('<L',ani_bytes[LIST_item_size+4:LIST_item_size+8])[0]
							if info_section == 'icon': 
								icon.append({
									'index' : icon_count,
									#ICONDIR
									'rtIconDir' : {
									'res' : struct.unpack('<H',ani_bytes[LIST_item_size+8:LIST_item_size+10])[0],
									'ico_type' : struct.unpack('<H',ani_bytes[LIST_item_size+10:LIST_item_size+12])[0],
									'ico_num_images' : struct.unpack('<H',ani_bytes[LIST_item_size+12:LIST_item_size+14])[0]
									},
									#ICONDIRENTRY
									'rtIconDirEntry' : {
									'bWidth'       : ani_bytes[LIST_item_size+14], # Width, in pixels, of the image
									'bHeight'      : ani_bytes[LIST_item_size+15], # Height, in pixels, of the image
									'bColorCount'  : ani_bytes[LIST_item_size+16], # Number of colors in image (0 if >=8bpp)
									'bReserved'    : ani_bytes[LIST_item_size+17], # Reserved
									'wPlanes'      : struct.unpack('<H',ani_bytes[LIST_item_size+18:LIST_item_size+20])[0], # Color Planes (or hotspot X coords for cur)
									'wBitCount'    : struct.unpack('<H',ani_bytes[LIST_item_size+20:LIST_item_size+22])[0], # Bits per pixel
									'dwBytesInRes' : struct.unpack('<L',ani_bytes[LIST_item_size+22:LIST_item_size+26])[0], # how many bytes in this resource?
									'dwDIBOffset'  : struct.unpack('<H',ani_bytes[LIST_item_size+26:LIST_item_size+28])[0] # RT_ICON rnID
									},
									'ico_file' : ani_bytes[LIST_item_size+8:LIST_item_size + list_chunk_size + 8]
								})
							icon_count += 1
							#print(info_section, hex(LIST_item_size), list_chunk_size)
							if (list_chunk_size % 2) != 0: # Yay DWORD boundaries
								list_chunk_size = list_chunk_size + 1
							LIST_item_size = LIST_item_size + list_chunk_size + 8
							
					
				total_size = total_size + chunk_size # The 8 accounts for the chunk id and size which is not included in the size
				
			
		else:
			self.logger.error("No RIFF ID, is {} an ANI file?".format(file_name))
			self.logger.debug("{:<21} | RIFF ID: {}, Form: {}".format("", ckID, ckForm))


		if INFO:
			for i in INFO:
				self.logger.debug("{:<21} | {:<21} | {}".format("",i, INFO[i]))
		if anih: 
			for i in anih:
				self.logger.debug("{:<21} | {:<21} | {}".format("",i, anih[i]))
		for section in icon:
				if section['index']:
					self.logger.debug("{:<21} | Index: {}".format("",section['index']))
					self.logger.debug("{:<21} | rtIconDir".format(""))
					for j in section['rtIconDir']:
						self.logger.debug("{:<21} | {:<21} | {}".format("",j, section['rtIconDir'][j]))
					self.logger.debug("{:<21} | rtIconDirEntry".format(""))
					for j in section['rtIconDirEntry']:
						self.logger.debug("{:<21} | {:<21} | {}".format("",j, section['rtIconDirEntry'][j]))

		cursor = {
			'INFO' : INFO,
			'anih' : anih,
			'seq'  : seq,
			'rate' : rate,
			'icon' : icon 
		}

		return cursor


	def convert_icon(self, target_folder, icon_file_path, tmp_file=work_dir + "/chicago95_tmp_file.svg"):
		## Converts Icons to PNG
		# Input:
		#  folder: svg file destination folder
		#  icon_file_path: theme icon file to be processed
		#  tmp_file: tmp working file for inkscape

		# Lots of code lifted from pixel2svg

		path_to_icon, icon_file_name = os.path.split(icon_file_path)
		icon_name, icon_ext = os.path.splitext(icon_file_name)
		svg_name = icon_name+".svg"

		if not os.path.exists(icon_file_path):
			# get the actual filename
			icon_file_path = [self.theme_files[i] for i in self.theme_files if icon_file_path in i][0]
		
		self.logger.debug("{:<21} | Converting {} to {} using pixel2svg".format("", icon_file_path, svg_name))
		# Open the icon file
		try:
			image = Image.open(icon_file_path)
		except IOError:
			self.logger.debug("{:<21} | Image BMP compression not support, converting".format(""))
			self.convert_ico_files(icon_file_path,"tmpimage.png")
			image = Image.open("tmpimage.png")
			os.remove("tmpimage.png")


		image = image.convert("RGBA")
		(width, height) = image.size
		rgb_values = list(image.getdata())
		rgb_values = list(image.getdata())
		svgdoc = svgwrite.Drawing(filename = target_folder + svg_name,
			                  size = ("{0}px".format(width * self.squaresize),
			                  "{0}px".format(height * self.squaresize)))

		rectangle_size = ("{0}px".format(self.squaresize + self.overlap),
			          "{0}px".format(self.squaresize + self.overlap))
		rowcount = 0
		while rowcount < height:
			colcount = 0
			while colcount < width:
				rgb_tuple = rgb_values.pop(0)
				# Omit transparent pixels
				if rgb_tuple[3] > 0:
					rectangle_posn = ("{0}px".format(colcount * self.squaresize),
						  "{0}px".format(rowcount * self.squaresize))
					rectangle_fill = svgwrite.rgb(rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])

					# Use CSS classes as a workaround for missing selectSameFillColor in Inkscape 1.2 and above
					rectangle_class = "r" + str(rgb_tuple[0]) + "-" + str(rgb_tuple[1]) + "-" + str(rgb_tuple[2]) + "-" + str(rgb_tuple[3])

					alpha = rgb_tuple[3]
					if alpha == 255:
						svgdoc.add(svgdoc.rect(insert = rectangle_posn,
						           size = rectangle_size,
						           fill = rectangle_fill,
								   class_ = rectangle_class))
					else:
						svgdoc.add(svgdoc.rect(insert = rectangle_posn,
				  	        	 size = rectangle_size,
				  	        	 fill = rectangle_fill,
				  		         opacity = alpha/float(255,
								 class_ = rectangle_class)))
				colcount = colcount + 1
			rowcount = rowcount + 1
		svgdoc.save()
		self.logger.debug("{:<21} | Prelim SVG created: {}".format("", target_folder + svg_name))

		self.convert_to_proper_svg_with_inkscape(tmp_file, svgdoc.filename)
		SVG_NS = "http://www.w3.org/2000/svg"
		svg = ET.parse(tmp_file)
		rects = svg.findall('.//{%s}rect' % SVG_NS)
		rgbs = {}
		for rect in rects:
			rect_id = rect.attrib['id']
			rgb = rect.attrib['fill']
			rect_class = rect.attrib['class']
			# Add both the rectangle ID and and rectangle class in an array case of Inkscape version issues
			if rgb not in rgbs:
				rgbs[rgb] = [rect_id, rect_class]

		
		self.logger.info("{:<21} | Inkscape will open {} times to process {}".format("", min(len(rgbs), self.max_colors), target_folder + svg_name))
		
		count = 0
		for rgb in rgbs:
			count = count + 1
			if len(rgbs) >= self.max_colors:
				self.logger.debug("{:<21} | Max colors ({}) hit exiting conversion".format("", self.max_colors))
				break
			self.logger.info("{:<21} | [{:<3} / {:<3} {:<5}] Converting {}".format("", count, len(rgbs),str(round((float(count)/float(len(rgbs))*100),0)), rgb ))
			self.fix_with_inkscape( rgbs[rgb] , tmp_file )

		shutil.move(tmp_file, svgdoc.filename)
		return(svgdoc.filename)

## Image functions

	def convert_to_proper_svg_with_inkscape(self, svg_out, svg_in):
		self.logger.debug("{:<21} | Converting {} to {} with Inkscape".format("",svg_out, svg_in))
		
		# this is a bit of a hack to support both version of inkscape

		if int(self.inkscape_info.version[0]) < 1:
			self.logger.debug("{:<21} | Using Inkscape v0.9x command".format(''))
			# Works with version 0.9x
			args = [
			self.inkscape_info.path,
			"-l", svg_out, svg_in
			]
		else:
			self.logger.debug("{:<21} | Using Inkscape v1.0 command".format(''))
			#works with version 1.0
			args = [
			self.inkscape_info.path,
			"-l", "-o", svg_out, svg_in
			]

		subprocess.check_call(args, stderr=subprocess.DEVNULL ,stdout=subprocess.DEVNULL)
		

	def fix_with_inkscape(self, color, tmpfile):
		self.logger.debug("{:<21} | Combining {} in {}".format("",color, tmpfile))
		
		if int(self.inkscape_info.version[0]) > 0:
			#The --verb option was removed from Inkscape 1.2, so versions newer than 1.1 must use the --actions command instead
			if int(self.inkscape_info.version[1]) > 1:
				args = [
					self.inkscape_info.path,
					"--batch-process",
					"--actions",
					"select-by-selector:."+color[1]+";object-to-path;path-union;export-overwrite:1;export-plain-svg:1;export-filename:"+tmpfile+";export-do;",
					tmpfile
				]
				print(" ".join(args))
			else:
				args = [
				self.inkscape_info.path,
				"-g",
				"--select="+color[0],
				"--verb", "EditSelectSameFillColor;SelectionCombine;SelectionUnion;FileSave;FileQuit",
				tmpfile
				]
		else:
			args = [
				self.inkscape_info.path,
				"--select="+color[0],
				"--verb", "EditSelectSameFillColor",
				"--verb", "SelectionCombine", 
				"--verb", "SelectionUnion", 
				"--verb", "FileSave", 
				"--verb", "FileQuit",
				tmpfile
				]

		subprocess.check_call(args, stderr=subprocess.DEVNULL ,stdout=subprocess.DEVNULL)

	def convert_to_png_with_inkscape(self, svg_in, size, png_out):
		self.logger.debug("{:<21} | Converting {} to {} of size {}".format("", svg_in, png_out, size))
		size = str(size)

		if int(self.inkscape_info.version[0]) < 1:
			args = [
			self.inkscape_info.path,
			"--without-gui",
			"-f", svg_in,
			"--export-area-page",
			"-w", size,
			"-h", size,
			"--export-png=" + png_out
			]
		else:
			args = [
			self.inkscape_info.path,
			"--export-area-page",
			"--export-type=png",
			"-w", size,
			"-h", size,
			"-o", png_out,
			svg_in
			]


		subprocess.check_call(args, stderr=subprocess.DEVNULL ,stdout=subprocess.DEVNULL)

	def get_inkscape_info(self):
		inkscape_path = subprocess.check_output(["which", "inkscape"]).strip().decode()

		inkscape_version_cmd = subprocess.check_output([inkscape_path, "--version"])
		inkscape_version = inkscape_version_cmd.splitlines()[0].split()[1].decode().split(".")[0:2]

		self.inkscape_info = inkscape_info(inkscape_path, inkscape_version)

	def convert_ico_files(self, icon_filename, output_file_name):
		self.logger.debug("{:<21} | Converting {} to {}".format("", icon_filename, output_file_name))
		convert_path = subprocess.check_output(["which", "convert"]).strip()
		#self.logger.info("{:<21} | {}".format(os.path.split(icon_filename)[1], os.path.split(output_file_name)[1]))
		args = [
		convert_path,
		icon_filename,
		output_file_name
		]
		subprocess.check_call(args)
		

	def convert_cur_files(self, cursor_filename, output_file_name):
		self.logger.debug("{:<21} | Converting {} to {}".format("", cursor_filename, output_file_name))
		convert_path = subprocess.check_output(["which", "convert"]).strip()
		self.logger.debug("{:<21} | {}".format(os.path.split(cursor_filename)[1], os.path.split(output_file_name)[1]))
		args = [
		convert_path,
		cursor_filename,
		output_file_name
		]
		subprocess.check_call(args)
		if  os.path.isfile(output_file_name[:-4]+"-0.png"):
			shutil.move(output_file_name[:-4]+"-0.png", output_file_name[:-4]+".png")

	def build_cursors(self, cursor_folder):
		self.logger.debug("Generating x11 cursor in {}".format(cursor_folder + "cursors/"))
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

		
		xcursorgen_path = subprocess.check_output(["which", "xcursorgen"]).strip()
		src_folder = cursor_folder + "src/"
		build_folder = cursor_folder + "cursors/"
		shutil.rmtree(build_folder)
		os.mkdir(build_folder)
		for gen in xcursors_conf:
			conf_file = src_folder + gen[3:]
			cursor_file_output = build_folder + xcursors_conf[gen]
			self.logger.debug("Building {:<21} | {}".format(os.path.split(conf_file)[1], os.path.split(cursor_file_output)[1]))
			args = [
				xcursorgen_path,
				"-p",
				src_folder,
				conf_file,
				cursor_file_output
			]
			subprocess.check_call(args, stdout=subprocess.DEVNULL)
#### Helper functions

	def font_name( self, font ):
	# From http://www.starrhorne.com/2012/01/18/how-to-extract-font-names-from-ttf-files-using-python-and-our-old-friend-the-command-line.html
		self.logger.debug("Getting font names")
		# Get font name and family
		FONT_SPECIFIER_NAME_ID = 4
		FONT_SPECIFIER_FAMILY_ID = 1
		name = ""
		family = ""
		for record in font['name'].names:
			self.logger.debug("Font record: {} ({})".format(record, record.nameID))
			if b'\x00' in record.string:
				try:
					name_str = record.string.decode('utf-16-be')
				except UnicodeDecodeError:
					name_str = record.string.decode('latin-1')
			else:   
				try:
					name_str = record.string.decode('utf-8')
				except UnicodeDecodeError:
					name_str = record.string.decode('latin-1')

			if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
				name = name_str
			elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family: 
				family = name_str
			if name and family: break
		return name, family


	def splitall(self, path):
		allparts = []
		while 1:
			parts = os.path.split(path)
			if parts[0] == path:  # sentinel for absolute paths
				allparts.insert(0, parts[0])
				break
			elif parts[1] == path: # sentinel for relative paths
				allparts.insert(0, parts[1])
				break
			else:
				path = parts[0]
				allparts.insert(0, parts[1])
		return allparts

	def get_icon_file_name(self, section, key, ignore_windir = False):
		#input:
		#  section = the section in the config file
		#  key     = key in theme file
		# Returns: filename

		reg_key = "Software\\Classes\\"
		file_name = ''
		icon_number = 0
		if section in self.config and key in self.config[section]:
			if isinstance(self.config[section][key], list):
				file_name = self.config[section][key][0].lower()
			else:
				file_name = self.config[section][key].lower()
		elif reg_key+section in self.config and key in self.config[reg_key+section]:
			file_name = self.config[reg_key+section][key].lower()
		else:
			return False

		if file_name == '':
			# The key was here but its empty
			return False

		if "%windir%" in file_name and not ignore_windir:
			# we dont bother changing system icons
			return False
		
		if "%ThemeDir%".lower() in file_name:
			file_name = file_name.replace("%ThemeDir%".lower(),'')
		
		if "," in file_name: 
			if len(file_name.split(",")) >= 3:
				loc = file_name.find(",", file_name.find(",")+1)	
				icon_number = file_name[loc:]
				file_name = file_name[:loc]
			else:
				file_name, icon_number = file_name.split(",")
		file_name = file_name.split("\\")[-1]
		self.logger.debug("section {}, key: {}, filename: {}".format(section, key, file_name))

		return (file_name, icon_number)

	def get_file_name(self, section, key, ignore_windir = False):
		#input:
		#  section = the section in the config file
		#  key     = key in theme file
		# Returns: filename

		reg_key = "Software\\Classes\\"
		file_name = ''
		icon_number = 0
		if section in self.config and key in self.config[section]:
			if isinstance(self.config[section][key], list):
				file_name = self.config[section][key][0].lower()
			else:
				file_name = self.config[section][key].lower()
		elif reg_key+section in self.config and key in self.config[reg_key+section]:
			file_name = self.config[reg_key+section][key].lower()
		else:
			return False

		if file_name == '':
			# The key was here but its empty
			return False

		if "%windir%" in file_name and not ignore_windir:
			# we dont bother changing system icons
			return False
		else:
			file_name = file_name.replace("%windir%".lower(),'')
		
		if "%ThemeDir%".lower() in file_name:
			file_name = file_name.replace("%ThemeDir%".lower(),'')
		
		file_name = file_name.split("\\")[-1]
		self.logger.debug("section {}, key: {}, filename: {}".format(section, key, file_name))

		return file_name

	def null_string(self, data):
		data = bytearray(data)
		try:
			string = data[:data.find(0)].decode('cp1252')
		except UnicodeDecodeError:
			string = data[:data.find(0)].decode('latin-1')

		return string

## Install functions

	def install_theme(self, cursors=True, icons=True, wallpaper=True, sounds=True, colors=True, fonts=True, screensaver=True):
		self.logger.info("Installing {}".format(self.theme_name))
		if cursors:
			self.install_cursors()
		if icons:
			self.install_icons()
		if fonts:
			self.install_fonts()		
		if wallpaper:
			self.install_wallpaper()
		if sounds:
			self.install_sounds()
		if colors:
			self.install_color_theme()
		if screensaver:
			self.logger.info("Screensavers require manual install. See the script in {}".format(self.folder_names['screensaver']))

	def install_cursors(self, cursor_dir=False, os_cursor_dir=str(Path.home())+"/.icons/"):
		self.logger.info("Installing cursors")
		if not os.path.exists(os_cursor_dir):
			self.logger.error("Cursor install directory does not exists: {}".format(os_cursor_dir))
			return

		if not cursor_dir:
			cursor_dir = self.folder_names['cursors']

		install_cursors_dir = os_cursor_dir + cursor_dir.split("/")[-2]

		self.logger.debug('Installing {} cursors to {}'.format(cursor_dir,install_cursors_dir))

		shutil.rmtree(install_cursors_dir, ignore_errors=True)
		shutil.copytree(self.folder_names['cursors'],install_cursors_dir,symlinks=True,ignore_dangling_symlinks=True)

	def install_icons(self, icons_dir=False, os_icons_dir=str(Path.home())+"/.icons/"):
		self.logger.info("Installing icons")
		
		if not os.path.exists(os_icons_dir):
			self.logger.error("Icons install directory does not exists: {}".format(os_icons_dir))
			return

		if not icons_dir:
			icons_dir = self.folder_names['icons']

		install_icons_dir = os_icons_dir + icons_dir.split("/")[-2]

		self.logger.debug('Installing {} icons to {}'.format(icons_dir,install_icons_dir))

		shutil.rmtree(install_icons_dir, ignore_errors=True)
		shutil.copytree(self.folder_names['icons'],install_icons_dir,symlinks=True,ignore_dangling_symlinks=True)
		

	def install_color_theme(self, color_theme_dir=False, os_theme_dir=str(Path.home())+"/.themes/"):
		self.logger.info("Installing color theme")
		
		if not os.path.exists(os_theme_dir):
			self.logger.error("Theme install directory does not exists: {}".format(os_theme_dir))
			return

		if not color_theme_dir:
			color_theme_dir = self.folder_names['theme']

		install_theme_dir = os_theme_dir + color_theme_dir.split("/")[-2]

		self.logger.debug('Installing {} colors to {}'.format(color_theme_dir,install_theme_dir))

		shutil.rmtree(install_theme_dir, ignore_errors=True)
		shutil.copytree(self.folder_names['theme'],install_theme_dir,symlinks=True,ignore_dangling_symlinks=True)

	def install_fonts(self, fonts_dir=False, os_fonts_dir=str(Path.home())+"/.fonts/"):
		self.logger.info("Installing fonts")
		
		if not os.path.exists(os_fonts_dir):
			self.logger.error("Theme install directory does not exists: {}".format(os_fonts_dir))
			return

		if not fonts_dir:
			fonts_dir = self.folder_names['fonts']

		install_theme_dir = os_fonts_dir + fonts_dir.split("/")[-2]

		self.logger.debug('Installing {} fonts to {}'.format(fonts_dir,install_theme_dir))

		shutil.rmtree(install_theme_dir, ignore_errors=True)
		shutil.copytree(self.folder_names['fonts'],install_theme_dir,symlinks=True,ignore_dangling_symlinks=True)

	def install_sounds(self, sounds_dir=False, os_sounds_dir=str(Path.home())+"/.local/share/sounds/"):
		self.logger.info("Installing sounds")

		if not os.path.exists(os_sounds_dir):
			self.logger.error("Theme install directory does not exists: {}".format(os_sounds_dir))
			return

		if not sounds_dir:
			sounds_dir = self.folder_names['sounds']

		install_theme_dir = os_sounds_dir + sounds_dir.split("/")[-2]

		self.logger.debug('Installing {} sounds to {}'.format(sounds_dir,install_theme_dir))

		shutil.rmtree(install_theme_dir, ignore_errors=True)
		shutil.copytree(self.folder_names['sounds'],install_theme_dir,symlinks=True,ignore_dangling_symlinks=True)

	def install_wallpaper(self, os_wallpaper_dir=str(Path.home()) + "/Pictures/"):
		"""
		Install the wallpaper by copying it to the designated directory and applying it
		to all monitors and workspaces dynamically.
		"""
		self.logger.info("Installing and applying wallpaper.")
		
		# Ensure the destination directory exists
		if not os.path.exists(os_wallpaper_dir):
			self.logger.error(f"Theme install directory does not exist: {os_wallpaper_dir}")
			return

		# Install the main wallpaper
		if (self.theme_config['wallpaper']['theme_wallpaper'] and
			self.theme_config['wallpaper']['theme_wallpaper']['wallpaper'] and
			self.theme_config['wallpaper']['theme_wallpaper']['path']):
			
			wallpaper_path = os.path.join(os_wallpaper_dir, self.theme_config['wallpaper']['theme_wallpaper']['new_filename'])
			self.logger.debug(f"Copying wallpaper from {self.theme_config['wallpaper']['theme_wallpaper']['path']} to {wallpaper_path}")
			try:
				shutil.copy(self.theme_config['wallpaper']['theme_wallpaper']['path'], wallpaper_path)
				self.logger.info(f"Wallpaper successfully installed to {wallpaper_path}")
			except Exception as e:
				self.logger.error(f"Could not install wallpaper to {wallpaper_path}: {e}")
				return

			# Apply the wallpaper to all monitors and workspaces
			self.apply_wallpaper_to_all_monitors(wallpaper_path, self.theme_config['wallpaper']['theme_wallpaper']['wallpaperstyle'])

		# Install additional wallpapers
		if self.theme_config['wallpaper']['extra_wallpapers']:
			for wallpaper in self.theme_config['wallpaper']['extra_wallpapers']:
				dest = os.path.join(os_wallpaper_dir, os.path.basename(wallpaper))
				self.logger.debug(f"Copying extra wallpaper from {wallpaper} to {dest}")
				try:
					shutil.copy(wallpaper, dest)
					self.logger.info(f"Extra wallpaper successfully installed to {dest}")
				except Exception as e:
					self.logger.error(f"Could not install extra wallpaper to {dest}: {e}")

	def apply_wallpaper_to_all_monitors(self, wallpaper_path, wallpaper_style):
		"""
		Apply the wallpaper to all monitors and workspaces dynamically.
		
		Args:
			wallpaper_path (str): Path to the wallpaper image.
			wallpaper_style (int): Wallpaper style (e.g., 0 = centered, 2 = stretched).
		"""
		channel = "xfce4-desktop"
		self.logger.info(f"Applying wallpaper '{wallpaper_path}' to all monitors and workspaces.")
		
		try:
			xfconf_query_path = subprocess.check_output(["which", "xfconf-query"]).strip()
			properties = subprocess.check_output(
				[xfconf_query_path, "--channel", channel, "--list"],
				universal_newlines=True
			).splitlines()

			# Filter relevant properties for workspaces and monitors
			for prop in properties:
				if "workspace" in prop and "last-image" in prop:
					workspace_base = prop.rsplit("/", 1)[0]  # Get base workspace path
					last_image_property = f"{workspace_base}/last-image"
					image_style_property = f"{workspace_base}/image-style"

					# Set wallpaper
					self.logger.debug(f"Setting wallpaper for {last_image_property} to {wallpaper_path}")
					subprocess.check_call(
						[xfconf_query_path, "--channel", channel, "--property", last_image_property, "--set", wallpaper_path]
					)

					# Set wallpaper style
					self.logger.debug(f"Setting image style for {image_style_property} to {wallpaper_style}")
					subprocess.check_call(
						[xfconf_query_path, "--channel", channel, "--property", image_style_property, "--set", str(wallpaper_style)]
					)
					
			self.logger.info("Wallpaper applied successfully.")

		except subprocess.CalledProcessError as e:
			self.logger.error(f"Failed to set wallpaper properties: {e}")
		except Exception as e:
			self.logger.error(f"Unexpected error while applying wallpaper: {e}")
				
	## Enable the theme in XFCE
	def enable_theme(self, cursors=True, icons=True, wallpaper=True, sounds=True, colors=True, fonts=True, screensaver=True):

		self.logger.info("Enabling {}".format(self.theme_name))
		if cursors:
			self.logger.info("Enabling New Cursors")
			# /Gtk/CursorThemeName
			# /Gtk/CursorThemeSize TODO: Can we use this for HDPI themes?
			self.xfconf_query('xsettings', '/Gtk/CursorThemeName', self.theme_name+"_Cursors")
		if icons:
			self.logger.info("Enabling New Icons")
			# /Net/FallbackIconTheme
			# /Net/IconThemeName
			self.xfconf_query('xsettings', '/Net/FallbackIconTheme', 'Chicago95')
			self.xfconf_query('xsettings', '/Net/IconThemeName', self.theme_name+"_Icons")
		if fonts:
			self.enable_fonts()		
		if wallpaper:
			# image-style 2 == Tiled
			# image-style 4 == Scaled
			# image-style 3 == Streched
			self.logger.info("Enabling New Wallpaper")
			if self.theme_config['wallpaper']['theme_wallpaper'] and self.theme_config['wallpaper']['theme_wallpaper']['new_filename']:
				try:
				# If we're using a VM the wallpaper is different				
					self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitorVirtual1/workspace0/last-image', str(Path.home()) + "/Pictures/" + self.theme_config['wallpaper']['theme_wallpaper']['new_filename'])

					if self.theme_config['wallpaper']['theme_wallpaper']['tilewallpaper']:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitorVirtual1/workspace0/image-style', "2")
					elif self.theme_config['wallpaper']['theme_wallpaper']['wallpaperstyle'] == 2:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitorVirtual1/workspace0/image-style', "3")
					else:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitorVirtual1/workspace0/image-style', "4")
				except:
					self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitor0/workspace0/last-image', str(Path.home()) + "/Pictures/" + self.theme_config['wallpaper']['theme_wallpaper']['new_filename'])

					if self.theme_config['wallpaper']['theme_wallpaper']['tilewallpaper']:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitor0/workspace0/image-style', "2")
					elif self.theme_config['wallpaper']['theme_wallpaper']['wallpaperstyle'] == 2:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitor0/workspace0/image-style', "3")
					else:
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitor0/workspace0/image-style', "4")
			else:
				self.logger.debug("Wallpaper failed to install")
				
		if sounds:
			self.logger.info("Enabling New Sounds")
			self.xfconf_query('xsettings', '/Net/SoundThemeName', self.theme_name+"_Sounds")
		if colors:
			self.logger.info("Enabling New Color Scheme")
			self.xfconf_query('xfwm4', '/general/theme', self.theme_name+"_Theme")
			self.xfconf_query('xsettings', '/Net/ThemeName', self.theme_name+"_Theme")
		if screensaver:
			self.logger.info("Screensavers require manual install. See the script in {}".format(self.folder_names['screensaver']))

		self.logger.info("Theme installation completed successfully!")
	

	def enable_fonts(self):
			# /Gtk/FontName "Family name and size" <- this is used for the other fonts, not titlebars

			# Typical fonts based on anaylisis of over 8,000 fonts to find most used fonts and linux equivalent
			# These font are typically included with Xubuntu installs
			# The check is:
			# 1 - Is the font family installed? If so just use that
			# 2 - If not, check for the 15 most popular fonts and Xubuntu alternatives
			# 3 - Otherwise use Sans, inform the user and give a link to fontworld/check the theme folder, install the font then rerun plus
			font_weights = {
				"FW_DONTCARE" : "0",
				"FW_THIN" : "100",
				"FW_EXTRALIGHT" : "200",
				"FW_ULTRALIGHT" : "200",
				"FW_LIGHT" : "300",
				"FW_NORMAL" : "400",
				"FW_REGULAR" : "400",
				"FW_MEDIUM" : "500",
				"FW_SEMIBOLD" : "600",
				"FW_DEMIBOLD" : "600",
				"FW_BOLD" : "700",
				"FW_EXTRABOLD" : "800",
				"FW_ULTRABOLD" : "800",
				"FW_HEAVY" : "900",
				"FW_BLACK" : "1000"
			}

			font_replacements = {
			"MS Sans Serif" : "Sans",
			"Arial" : "Liberation Sans",
			"Times New Roman" : "Liberation Serif",
			"Tahoma" : "Kalimati",
			"News Gothic MT" : "News Cycle",
			"Abadi MT Condensed Light" : "",
			"Century Gothic" : "League Gothic",
			"Verdana" : "Kalimati",
			"Microsoft Sans Serif" : "Sans",
			"Arial Narrow" : "Liberation Narrow",
			"Copperplate Gothic Light" : "League Gothic",
			"Impact" : "League Gothic",
			"MS Serif" : "Sans",
			"‚l‚r ‚oƒSƒVƒbƒN" : "Sans",
			"Courier New" : "Liberation Mono",
			"Georgia" : "Rekha",
			"Lucida Grande" : "Garuda"	
			}

			self.logger.info("Enabling New Fonts")
			self.get_font_list()
			if 'nonclientmetrics' in self.theme_config:
				
				try:
					xfconf_query_path = subprocess.check_output(["which", "xfconf-query"]).strip()
					self.logger.debug("Getting DPI")
					args = [
						xfconf_query_path,
						"-v", '-l', '-c', 'xsettings',
						"-p", '/Xft/DPI'
						]
					dpi = subprocess.check_output(args).split()[1]
				
				except subprocess.CalledProcessError:
					self.logger.info("xfconf not installed, enable theme manually")
					return

				self.logger.debug("Getting MenuFont and CaptionFont")
				for logfont in ['lfcaptionfont', 'lfMenuFont']:
					if isinstance(self.theme_config['nonclientmetrics'][logfont], dict) and 'lfFaceName[32]' in self.theme_config['nonclientmetrics'][logfont]:

						font_family = self.theme_config['nonclientmetrics'][logfont]['lfFaceName[32]']
						lfheight = self.theme_config['nonclientmetrics'][logfont]['lfHeight']
						font_weight = font_weights[self.theme_config['nonclientmetrics'][logfont]['lfWeight']]
							
						if lfheight < 0:
							font_size = abs((lfheight / int(dpi)) * 72) #Per MS LOGFONT spec
						else:
							font_size = lfheight

						self.logger.debug("{:<21} | font: {} weight: {}".format(logfont, font_family, font_weight))

						installed_fonts = self.get_font_list()
						if font_family in installed_fonts:
							self.logger.debug("{:<21} | Font installed".format(font_family))
							font = font_family
						else:
							self.logger.debug("{:<21} | Font not installed searching for alternate".format(font_family))
							if font_family in font_replacements and font_replacements[font_family] in self.get_font_list():
								self.logger.debug("{:<21} | Replacement found for {}: {}".format("", font_family, font_replacements[font_family]))
								font = font_replacements[font_family]
							else:
								font = "Sans"
								self.logger.debug("{:<21} | No replacement found using Sans".format(''))
						if logfont == 'lfcaptionfont':
								lfcaptionfont = font

						if logfont == 'lfMenuFont' and font != lfcaptionfont and font != "Sans":
							self.logger.info("Menufont: font: {} weight: {}".format(font, font_weight))
									
							for gtk_menu in [ self.folder_names['theme']+"gtk-3.24/gtk-menu.css", self.folder_names['theme']+"gtk-3.0/gtk-menu.css"]:

								shutil.move( gtk_menu, gtk_menu+"~" )
								fileh = open(gtk_menu+"~","r")
								nfileh = open(gtk_menu,"w")
								for line in fileh:
									if '.menubar' in line:
										self.logger.debug("{:<21} | Adding menubar font to {}: {} weight: {}".format('', gtk_menu, font, font_weight))
										line = line.replace(line, line+"\n"+"  font-family: {};\n  font-weight: {};\n".format(font, font_weight))
									nfileh.write(line)
								fileh.close()
								nfileh.close()

								self.install_color_theme()

						elif logfont == 'lfcaptionfont':
							if font == "Sans":
								font = "Sans Bold"
							self.logger.info("Captionfont: font: {} weight: {}".format(font, font_weight))
							self.xfconf_query('xfwm4', '/general/title_font', font + ' 8')

## Enable Helper functions
	def xfconf_query(self, channel, prop_base, new_value):
		"""
		Dynamically sets xfconf properties for all monitors and workspaces.
		
		:param channel: The xfconf channel (e.g., "xfce4-desktop").
		:param prop_base: Base property path (e.g., "/backdrop/screen0").
		:param new_value: The new value to set for the property.
		"""
		try:
			xfconf_query_path = subprocess.check_output(["which", "xfconf-query"]).strip()
			self.logger.debug(f"Changing xfconf setting {channel}/{prop_base} to {new_value}")

			# Retrieve all properties in the channel
			props = subprocess.check_output(
				[xfconf_query_path, "--channel", channel, "--list"],
				universal_newlines=True
			).splitlines()

			# Filter relevant properties for monitors and workspaces
			for prop in props:
				if prop.startswith(prop_base):
					self.logger.debug(f"Found property: {prop}")

					# Update the property value
					args = [
						xfconf_query_path,
						"--channel", channel,
						"--property", prop,
						"--set", new_value
					]
					try:
						subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
						self.logger.info(f"Set {prop} to {new_value}")
					except subprocess.CalledProcessError as e:
						self.logger.error(f"Failed to set {prop}: {e}")

		except subprocess.CalledProcessError:
			self.logger.error("xfconf-query not installed or not available. Enable theme manually.")
		except Exception as e:
			self.logger.error(f"Error setting xfconf property: {e}")


	def get_font_list(self):
		fc_list = subprocess.check_output(["which", "fc-list"]).strip()
		fonts_output = subprocess.check_output([fc_list])
		

		fonts = []
		for font in fonts_output.decode().split('\n'):
			if len(font.split(":")) > 1 and font.split(":")[1] not in fonts:
				fonts.append(font.split(":")[1].strip())

		return(fonts)

	def logo(self):
		logo = '''
         
     || Chicago95         **
 ########  ##   ##       ****        
 ##  || ## ##   ## $$$$$$**** 
 ##  || ## ##   ##$$      ** 
 ########  ##   ## $$$$     
 ##  ||     #####      $$ **
 ##  ||||||||     $$$$$$  **
 ##                        
'''
		return logo

class inkscape_info:
	def __init__(self, path, version):
		self.path = path
		self.version = version