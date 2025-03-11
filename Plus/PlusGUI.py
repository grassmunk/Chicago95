#!/usr/bin/env python3

import sys
from pluslib import ChicagoPlus
import logging
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw, ImageEnhance, ImageOps
from pprint import pprint
import struct
import subprocess
import os
from shutil import copyfile
import textwrap
import numpy as np
import array
import argparse
import time

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib

running_folder = os.path.dirname(os.path.abspath(__file__))
share_dir = running_folder
libexec_dir = running_folder
work_dir = running_folder
if not os.path.exists(work_dir):
    os.makedirs(work_dir)

c95_packaged_cursor_path=str(Path.home())+"/.icons/Chicago95_Cursor_Black"
c95_packaged_theme_path=str(Path.home())+"/.themes/Chicago95"
c95_packaged_icons_path=str(Path.home())+"/.icons/Chicago95"

#print("Font List...", end=' ', flush=True)
fonts_output = subprocess.check_output(['convert', '-list', 'font'])
fonts = fonts_output.decode().split('\n')
installed_fonts = {}
for index, font in enumerate(fonts):
	if "Font:" in font:
		installed_fonts[fonts[index].split(":")[1].strip()] = {
			fonts[index+1].split(":")[0].strip() : fonts[index+1].split(":")[1].strip(), 
			fonts[index+2].split(":")[0].strip() : fonts[index+2].split(":")[1].strip(), 
			fonts[index+3].split(":")[0].strip() : fonts[index+3].split(":")[1].strip(), 
			fonts[index+4].split(":")[0].strip() : fonts[index+4].split(":")[1].strip(), 
			fonts[index+5].split(":")[0].strip() : fonts[index+5].split(":")[1].strip()
		}
#print("OK", end='\n', flush=True)
sys.stdout.flush()


pointers = {
	#windows theme  # Name
	"arrow"       : "Normal select",
	"help"        : "Help select",
	"appstarting" : "Working in background",
	"wait"        : "Busy",
	"crosshair"   : "Precision select",
	"ibeam"       : "Text Select",
	"nwpen"       : "Handwriting",
	"no"          : "NO",
	"sizens"      : "Vertical resize",
	"sizewe"      : "Horizontal resize",
	"sizenwse"    : "Diagonal resize 1",
	"sizenesw"    : "Diagonal resize 2",
	"sizeall"     : "Move",
	"uparrow"     : "Alternate select"
	}

icons = {
	# Windows Themes : #Name
	"my_computer" : "My Computer icon",
	"network_neighborhood" : "Network Neighborhood icon",
	"recycle_bin_full" : "Recycle Bin full icon",
	"recycle_bin_empty" : "Recycle Bin empty icon",
	"my_documents" : "My Documents icon"
	}

sounds = { 
	'SystemAsterisk' : 'Asterisk',
	'Close' : 'Close program',
	'SystemHand' : 'Critical stop',
	'.Default' : 'Default beep',
	'SystemDefault' : 'Default sound',
	'EmptyRecycleBin' : 'Empty Recylcle Bin',
	'SystemExclamation' : 'Exclamation',
	'SystemExit' : 'Exit Windows',
	'Maximize' : 'Maximize',
	'MenuCommand' : 'Menu command',
	'MenuPopup' : 'Menu popup',
	'Minimize' : 'Minimize',
	'Open' : 'Open program',
	'AppGPFault' : 'Program error',
	'SystemQuestion' : 'Question',
	'RestoreDown' : 'Restore down',
	'RestoreUp' : 'Restore up',
	'RingIn' : 'Ring in',
	'RingOut' : 'Ring out',
	'SystemStart' : 'Start Windows'
}



class MakePreview:
	def __init__(self, theme_object):
		#print("Reading theme file... {}".format(theme_file))
		print("[MakePreview] Generating Preview Image")
		self.plus = theme_object
		self.plus.parse_theme()
		self.set_metrics()
		self.set_fonts()
		self.get_icons()
		self.get_wallpaper()
		#self.plus.print_theme_config()

		self.colors = {
			"buttonface": "#C0C0C0",
			"buttontext": "#000000",
			"inactivetitle": "#808080",
			"inactivetitletext": "#DFDFDF",
			"inactiveborder": "#C0C0C0",
			"buttondkshadow": "#000000",
			"buttonshadow": "#808080",
			"buttonhilight": "#FFFFFF",
			"buttonlight": "#DFDFDF",
			"activetitle": "#000080",
			"titletext": "#FFFFFF",
			"activeborder": "#C0C0C0",
			"menutext": "#000000",
			"menu": "#C0C0C0",
			"hilighttext": "#FFFFFF",
			"hilight": "#000080",
			"window": "#FFFFFE",
			"windowtext": "#000000",
			"scrollbar": "#FFFFFF",
			"background": "#000000",
			"foreground": "#000000"
		}

		for i in self.colors:

			try:
				self.colors[i] = (self.plus.theme_config['colors'][i]['color'])
			except KeyError:
				continue

		self.colors['foreground'] = self.black_or_white(self.colors['background'])
		self.theme_name = self.plus.theme_config['theme_name']
		self.buttons()
		self.preview_gen()
#		pprint(self.colors)
		print("[MakePreview] Preview Generated")

	def return_preview(self):
		self.preview_window.save(work_dir+"/preview.png", "PNG")
		return(work_dir+"/preview.png")
		
	def return_preview_double(self):
		self.preview_window.save(work_dir+"/preview_double.png", "PNG")
		return(work_dir+"/preview_double.png")

	def delete_preview(self):
		os.remove(work_dir+"/preview.png")

	def delete_preview_double(self):
		os.remove(work_dir+"/preview_double.png")

	def set_fonts(self):
		print("[MakePreview] Fonts...", end=' ')
		self.button_height = self.iCaptionHeight - 4
		self.button_width = self.button_height + 2
		self.lfMessageFont = self.get_font(self.msgfont)
		self.lfcaptionfont = self.get_font(self.caption_font)
		self.lfMenuFont = self.get_font(self.menufont)
		self.arial = self.get_font("Nimbus Sans L")
		self.arial_bold = self.get_font("Nimbus-Sans-L-Bold")
		self.lfFont = self.get_font(self.iconfont)

		self.cursor_font = self.get_font("Nimbus-Sans-L-Bold")
		self.cursor_pt = 12
		print("OK", end='\n', flush=True)

	def buttons(self):
		print("[MakePreview] Buttons...", end=' ')
		buttons = ['minimize','maximize','close']
		button_width = self.button_width
		button_height = self.button_height
		colors = self.colors

		for button in buttons:

			img = Image.new('RGB', (button_width, button_height), color = colors['buttondkshadow'])
			draw = ImageDraw.Draw(img)
			draw.line([(0,0),(button_width-2, 0), (0,0),(0, button_height-2)],fill=colors['buttonhilight'], width=1)

			draw.line([(button_width-2,button_height-2),(button_height, 1)],fill=colors['buttonshadow'], width=1)
			draw.line([(1,button_height-2),(button_width-2,button_height-2)],fill=colors['buttonshadow'], width=1)

			draw.line([(1,1),(button_width-3, 1), (1,1),(1, button_height-3)],fill=colors['buttonlight'], width=1)
			draw.rectangle(((2, 2), (button_width-3, button_height-3)), fill=colors['buttonface'], width=1)
			if button_height < 16:
				if button == "minimize":
					draw.line([(4,9),(10, 9)],fill=colors['buttontext'], width=2)
					self.min_button = img
				elif button == 'maximize':
					draw.line([(3,10),(11, 10)],fill=colors['buttontext'], width=1)
					draw.line([(3,2),(11, 2)],fill=colors['buttontext'], width=2)
					draw.line([(3,2),(3, 10)],fill=colors['buttontext'], width=1)
					draw.line([(11,2),(11, 10)],fill=colors['buttontext'], width=1)
					self.max_button = img
				elif button == 'close':
					img.putpixel( (4, 3), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (5, 3), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (5, 4), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (6, 4), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (6, 5), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (7, 5), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (7, 6), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (8, 6), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (8, 7), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (9, 7), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (9, 8), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (10, 8), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (10, 9), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (11, 9), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (4, 9), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (5, 9), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (5, 8), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (6, 8), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (6, 7), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (7, 7), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (7, 6), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (8, 6), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (8, 5), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (9, 5), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (9, 4), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (10, 4), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (10, 3), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					img.putpixel( (11, 3), tuple(int(colors['buttontext'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) )
					self.close_button = img

			else:
				if button == "minimize":
					draw.line([(5, button_height - 6),(button_width - 8,button_height - 6)],fill=colors['buttontext'], width=2)
					self.min_button = img
				elif button == 'maximize':
					draw.line([(4,button_height-5),(button_width - 6 , button_height - 5)],fill=colors['buttontext'], width=1)
					draw.line([(4,4),(button_width - 6, 4)],fill=colors['buttontext'], width=2)
					draw.line([(4,4),(4, button_height-5)],fill=colors['buttontext'], width=1)
					draw.line([(button_width - 6, 4),(button_width - 6, button_height-5)],fill=colors['buttontext'], width=1)
					self.max_button = img
				elif button == 'close':
					X = Image.open(share_dir+"/assets/X.png").convert('RGBA')
					pixels = X.load()
					rgb = struct.unpack('BBB',bytes.fromhex(colors['buttontext'].lstrip('#')))
					for i in range(X.size[0]):
						for j in range(X.size[1]):
							if pixels[i,j] == (0, 0, 0, 255):
								pixels[i,j] = rgb
					x_w, x_h = X.size
					offset = ((button_width - x_w) // 2, (button_height - x_h) // 2)
					img.paste(X, offset, mask=X)
					self.close_button = img
		
		print("OK", end='\n', flush=True)

	def set_metrics(self):

		print("[MakePreview] Metrics...", end=' ', flush=True)
		try:	
			self.iCaptionHeight = self.plus.theme_config['nonclientmetrics']['iCaptionHeight']
			self.iMenuHeight = self.plus.theme_config['nonclientmetrics']['iMenuHeight']
			self.iScrollWidth = self.plus.theme_config['nonclientmetrics']['iScrollWidth']
			self.msgfont = self.plus.theme_config['nonclientmetrics']['lfMessageFont']['lfFaceName[32]']
			self.msgfont_pt = abs(self.plus.theme_config['nonclientmetrics']['lfMessageFont']['lfHeight'])
			self.caption_font = self.plus.theme_config['nonclientmetrics']['lfcaptionfont']['lfFaceName[32]']
			self.caption_pt = abs(self.plus.theme_config['nonclientmetrics']['lfcaptionfont']['lfHeight'])
			self.menufont = self.plus.theme_config['nonclientmetrics']['lfMenuFont']['lfFaceName[32]']
			self.menufont_pt = abs(self.plus.theme_config['nonclientmetrics']['lfMenuFont']['lfHeight'])
		except:

			self.iCaptionHeight = 18
			self.iMenuHeight = 18
			self.iMenuWidth = 18
			self.iScrollHeight = 13
			self.iScrollWidth = 13
			self.msgfont = "Microsoft Sans Serif"
			self.caption_font = "MS-Reference-Sans-Serif-Bold"
			self.menufont = "Microsoft Sans Serif"
			self.menufont_pt = 10
			self.caption_pt = 10
			self.msgfont_pt = 10

		try:
			self.iconfont = self.plus.theme_config['iconmetrics']['lfFont']['lfFaceName[32]']
			self.iconfont_pt = abs(self.plus.theme_config['iconmetrics']['lfFont']['lfHeight'])
		except:
			self.iconfont = "Microsoft Sans Serif"
			self.iconfont_pt = 10
		if self.iconfont_pt == 8:
			self.iconfont_pt = 10

		if self.msgfont_pt == 8:
			self.msgfont_pt = 10

		if self.caption_pt == 8:
			self.caption_pt = 10

		if self.menufont_pt == 8:
			self.menufont_pt = 10
		print("OK", end='\n', flush=True)

	def get_icons(self):
		print("[MakePreview] Icons...", end=' ', flush=True)
		if self.plus.theme_config['icons']:
			if self.plus.theme_config['icons']['my_computer']:
				self.my_computer = self.make_icons(self.plus,'my_computer')
			else:
				self.my_computer = Image.open(share_dir+"/assets/my_computer~.png").convert('RGBA')

			if self.plus.theme_config['icons']['network_neighborhood']:
				self.network_neighborhood= self.make_icons(self.plus,'network_neighborhood')
			else:
				self.network_neighborhood = Image.open(share_dir+"/assets/network_neighborhood~.png").convert('RGBA')

			if self.plus.theme_config['icons']['recycle_bin_empty']:
				self.recycle_bin_empty = self.make_icons(self.plus,'recycle_bin_empty')
			else:
				self.recycle_bin_empty = Image.open(share_dir+"/assets/recycle_bin_empty~.png").convert('RGBA')
			
			if self.plus.theme_config['icons']['my_documents']:
				self.my_documents = self.make_icons(self.plus,'my_documents')
			else:
				self.my_documents = False
		print("OK", end='\n', flush=True)

	def drawlines(self, drawcontext, xy, outline=None, width=0):
		(x1, y1), (x2, y2) = xy
		points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
		drawcontext.line(points, fill=outline, width=width)

	def black_or_white(self, background_color):

		# Counting the perceptive luminance - human eye favors green color... 
		R, G, B = tuple(int(background_color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
		luminance = ( (0.299 * R) + (0.587 * G) + (0.114 * B))/255;
		if (luminance > 0.5):
			d = "#000000" # bright colors - black font
		else:
			d = "#FFFFFF" # dark colors - white font

		return  d

	def get_font(self, fontname):

		if self.plus.theme_config['fonts']:
			if fontname in self.plus.theme_config['fonts']:
				return self.plus.theme_config['fonts'][fontname]['path']


		if fontname in ["MS Sans Serif", "MS Serif", "‚l‚r ‚oƒSƒVƒbƒN"]:
			fontname = "Microsoft Sans Serif"

		if fontname in installed_fonts:
			#print("Found installed font {}: {}".format(fontname,installed_fonts[fontname]['glyphs']))
			return installed_fonts[fontname]['glyphs']

		elif fontname.replace(' ','-') in installed_fonts:
			return installed_fonts[fontname.replace(' ','-')]['glyphs']
			
		else:
			for i in installed_fonts:
				if fontname.lower() == i.lower():
					#print("Found installed font {}: {}".format(fontname,installed_fonts[i]['glyphs']))
					return installed_fonts[i]['glyphs']
				elif fontname.lower() in installed_fonts[i]['family'].lower():
					#print("Found installed font {}: {}".format(fontname,installed_fonts[i]['glyphs']))
					return installed_fonts[i]['glyphs']
				elif fontname.replace(' ','-').lower() in i.lower():
					#print("Found installed font {}: {}".format(fontname,installed_fonts[i]['glyphs']))
					return installed_fonts[i]['glyphs']

		#print("Font: {} NOT FOUND".format(fontname))
		
		return self.get_font("Noto-Sans-Regular")
	
	def get_font_y_offset(self, draw, text, font):
    # Get the top offset from the bounding box
		left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
		return top

	def preview_gen(self):
		print("[MakePreview] Preview...", end=' ', flush=True)
		colors = self.colors

		tmp = Image.new('RGB', (500, 500), color = colors['activetitle'])
		tmp_draw = ImageDraw.Draw(tmp)

		#This generates the Message Box title you see in the preview windoow
		msgboxtitle = Image.new('RGB', (173-6, self.iCaptionHeight), color = colors['activetitle']) 
		draw = ImageDraw.Draw(msgboxtitle)
		myFont = ImageFont.truetype(self.lfcaptionfont, self.caption_pt)
		#w, h = draw.textsize("Message Box", font=myFont)
		left, top, right, bottom = draw.textbbox((0, 0), "Message Box", font=myFont)
		w, h = right - left, bottom - top
		#font_y_offset = myFont.getoffset("Message Box")[1]
		font_y_offset = top
		draw.fontmode = "1"
		draw.text((2,int(((self.iCaptionHeight-h)-font_y_offset)/2)), "Message Box", fill=colors['titletext'], font=myFont)

		#This generates the Inactive Window title in the previre
		inactive_window = Image.new('RGB', (202, self.iCaptionHeight+118+3), color = colors['buttondkshadow'])
		inactivetitle = Image.new('RGB', (inactive_window.size[0]-8, self.iCaptionHeight), color = colors['inactivetitle']) 
		draw = ImageDraw.Draw(inactivetitle)
		myFont = ImageFont.truetype(self.lfcaptionfont, self.caption_pt)
		#w, h = draw.textsize("Inactive Window", font=myFont)
		left, top, right, bottom = draw.textbbox((0, 0), "Inactive Window", font=myFont)
		w, h = right - left, bottom - top

		font_y_offset = top
		draw.fontmode = "1"
		draw.text((2,int((self.iCaptionHeight-h)-font_y_offset)/2), "Inactive Window", fill=colors['inactivetitletext'], font=myFont)
		

		#Now we create the Active window title in multiple steps, starting with the title
		activetitle = Image.new('RGB', (217, self.iCaptionHeight), color = colors['activetitle']) 
		draw = ImageDraw.Draw(activetitle)
		myFont = ImageFont.truetype(self.lfcaptionfont, self.caption_pt)
		#font_y_offset = myFont.getoffset("Active Window")[1]
		#w, h = draw.textsize("Active Window", font=myFont)
		left, top, right, bottom = draw.textbbox((0, 0), "Active Window", font=myFont)
		w, h = right - left, bottom - top
		font_y_offset = top
		draw.fontmode = "1"
		draw.text((2,int((self.iCaptionHeight-h)-font_y_offset)/2), "Active Window", fill=colors['titletext'], font=myFont)

		#Next we draw the menubar
		menufont = ImageFont.truetype(self.lfMenuFont, self.menufont_pt)
		#normal_w, normal_h = tmp_draw.textsize("Normal", font=menufont)
		menubar = Image.new('RGB', (activetitle.size[0], self.iMenuHeight), color = colors['menu']) 
		draw = ImageDraw.Draw(menubar)
		#Normal menu item
		#normal_w, normal_h = draw.textsize("Normal", font=menufont)
		left, top, right, bottom = draw.textbbox((0, 0), "Normal", font=menufont)
		normal_w, normal_h = right - left, bottom - top
		#font_y_offset = menufont.getoffset("Normal")[1]
		font_y_offset = top
		draw.fontmode = "1"
		draw.text((6,int(((menubar.size[1]-normal_h)-font_y_offset)/2)), "Normal", fill=colors['menutext'], font=menufont)
		#Disabled menu item
		#disabled_w, disabled_h = draw.textsize("Disabled", font=menufont)
		left, top, right, bottom = draw.textbbox((0, 0), "Disabled", font=menufont)
		disabled_w, disabled_h = right - left, bottom - top
		draw.text((normal_w+14,(int(((menubar.size[1]-normal_h)-font_y_offset)/2))+1), "Disabled", fill=colors['buttonhilight'], font=menufont)
		draw.text((normal_w+13,int(((menubar.size[1]-normal_h)-font_y_offset)/2)), "Disabled", fill=colors['buttonshadow'], font=menufont)
		#Selected menu item
		#selected_w, selected_h = draw.textsize("Selected", font=menufont)
		left, top, right, bottom = draw.textbbox((0, 0), "Selected", font=menufont)
		selected_w, selected_h = right - left, bottom - top
		#myFont.fontmode = "1"
		#draw.text((6,int(menubar.size[1]-normal_h)/2), "Selected", fill=colors['hilighttext'], font=menufont)
		selected = Image.new('RGB', (selected_w+12,menubar.size[1]), color = colors['hilight'])
		selected_draw = ImageDraw.Draw(selected)
		selected_draw.fontmode = "1"
		#font_y_offset = menufont.getoffset("Selected")[1]
		font_y_offset = top
		selected_draw.text((int((selected.size[0]-selected_w)/2),int(((menubar.size[1]-normal_h)-font_y_offset)/2)), "Selected", fill=colors['hilighttext'], font=menufont)
		menubar.paste(selected, (normal_w+13+disabled_w+6,int((menubar.size[1]-selected.size[1])/2)))

		#Now we need to create the scrollbar, first up arrow
		uparrow = Image.new('RGB', (self.iScrollWidth, self.iScrollWidth), color = colors['buttonface'])
		draw = ImageDraw.Draw(uparrow)
		draw.line([(0,0),(uparrow.size[0]-2, 0), (0,0), (0,uparrow.size[1]-2)],fill=colors['buttonlight'], width=1)
		draw.line([(1,1),(uparrow.size[0]-3, 1), (1,1), (1,uparrow.size[1]-3)],fill=colors['buttonhilight'], width=1)
		draw.line([(uparrow.size[0]-1,uparrow.size[1]-1),(uparrow.size[0]-1, 0), (uparrow.size[0]-1,uparrow.size[1]-1), (0,uparrow.size[1]-1)],fill=colors['buttondkshadow'], width=1)
		draw.line([(uparrow.size[0]-2,uparrow.size[1]-2),(uparrow.size[0]-2, 1), (uparrow.size[0]-2,uparrow.size[1]-2), (1,uparrow.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.polygon([(4,7), (8,7), (6,5)], fill = colors['buttontext'])

		#Next down arrow
		downarrow = Image.new('RGB', (self.iScrollWidth, self.iScrollWidth), color = colors['buttonface'])
		draw = ImageDraw.Draw(downarrow)
		draw.line([(0,0),(downarrow.size[0]-2, 0), (0,0), (0,downarrow.size[1]-2)],fill=colors['buttonlight'], width=1)
		draw.line([(1,1),(downarrow.size[0]-3, 1), (1,1), (1,downarrow.size[1]-3)],fill=colors['buttonhilight'], width=1)
		draw.line([(downarrow.size[0]-1,downarrow.size[1]-1),(downarrow.size[0]-1, 0), (downarrow.size[0]-1,downarrow.size[1]-1), (0,downarrow.size[1]-1)],fill=colors['buttondkshadow'], width=1)
		draw.line([(downarrow.size[0]-2,downarrow.size[1]-2),(downarrow.size[0]-2, 1), (downarrow.size[0]-2,downarrow.size[1]-2), (1,downarrow.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.polygon([(4,5), (8,5), (6,7)], fill = colors['buttontext'])

		#With all the pieces done we can now create the scroll area
		window = Image.new('RGB', (217, 72), color = colors['window'])
		draw = ImageDraw.Draw(window)
		draw.line([(0,0),(window.size[0]-2, 0), (0,0), (0,window.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.line([(1,1),(window.size[0]-3, 1), (1,1), (1,window.size[1]-3)],fill=colors['buttondkshadow'], width=1)
		draw.line([(window.size[0]-1,window.size[1]-1),(window.size[0]-1, 0), (window.size[0]-1,window.size[1]-1), (0,window.size[1]-1)],fill=colors['buttonhilight'], width=1)
		draw.line([(window.size[0]-2,window.size[1]-2),(window.size[0]-2, 1), (window.size[0]-2,window.size[1]-2), (1,window.size[1]-2)],fill=colors['buttonlight'], width=1)
		window_font = ImageFont.truetype(self.arial_bold, 14)
		draw.fontmode = "1"
		#font_y_offset = window_font.getoffset("Window Text")[1]
		font_y_offset = self.get_font_y_offset(draw, "Window Text", window_font)
		draw.text((4,7-font_y_offset), "Window Text", fill=colors['windowtext'], font=window_font)
		window.paste(uparrow, (window.size[0]-2-uparrow.size[0],2))
		draw.rectangle(((window.size[0]-2-uparrow.size[0],2+uparrow.size[1]),(window.size[0]-3, window.size[1]-3)), fill=colors['scrollbar'])
		window.paste(downarrow, (window.size[0]-2-downarrow.size[0],window.size[1]-2-downarrow.size[1]))

		#And with that we have all the peices to make the active window, first we make the window
		activewindow = Image.new('RGB', (225, 4+self.iCaptionHeight+1+self.iMenuHeight+1+window.size[1]+4), color = colors['buttonface'])
		draw = ImageDraw.Draw(activewindow)
		draw.line([(0,0),(activewindow.size[0]-2, 0), (0,0), (0,activewindow.size[1]-2)],fill=colors['buttonlight'], width=1)
		draw.line([(1,1),(activewindow.size[0]-3, 1), (1,1), (1,activewindow.size[1]-3)],fill=colors['buttonhilight'], width=1)
		draw.line([(activewindow.size[0]-1,activewindow.size[1]-1),(activewindow.size[0]-1, 0), (activewindow.size[0]-1,activewindow.size[1]-1), (0,activewindow.size[1]-1)],fill=colors['buttondkshadow'], width=1)
		draw.line([(activewindow.size[0]-2,activewindow.size[1]-2),(activewindow.size[0]-2, 1), (activewindow.size[0]-2,activewindow.size[1]-2), (1,activewindow.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.rectangle(((2, 2), (activewindow.size[0]-3, activewindow.size[1]-3)), fill=colors['activeborder'], width=1)
		draw.rectangle(((3, 3), (activewindow.size[0]-4, activewindow.size[1]-4)), fill=colors['buttonface'], width=1)
		#Then we put all the pieces inside		
		activewindow.paste(activetitle, (4,4))
		activewindow.paste(self.close_button, (activewindow.size[0]-self.close_button.size[0]-6, 6))
		activewindow.paste(self.max_button, (activewindow.size[0]-self.close_button.size[0]-6-2-self.max_button.size[0], 6))
		activewindow.paste(self.min_button, (activewindow.size[0]-self.close_button.size[0]-6-2-self.max_button.size[0]-self.min_button.size[0], 6))
		activewindow.paste(menubar, (4, 4+activetitle.size[1]+1))
		activewindow.paste(window, (4, 4+activetitle.size[1]+1+menubar.size[1]+1))

		# Next we create the message window, first making the 'ok' button
		button = Image.new('RGB', (66, 22), color = colors['buttondkshadow'])
		draw = ImageDraw.Draw(button)
		draw.line([(0,0),(64, 0), (0,0), (0,20)],fill=colors['buttonhilight'], width=1)
		draw.line([(button.size[0]-2,1),(button.size[0]-2,button.size[1]-2 )],fill=colors['buttonshadow'], width=1)
		draw.line([(1,button.size[1]-2),(button.size[0]-2,button.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.line([(1,1),(button.size[0]-3, 1), (1,1),(1, button.size[1]-3)],fill=colors['buttonlight'], width=1)
		draw.rectangle(((2, 2), (button.size[0]-3, button.size[1]-3)), fill=colors['buttonface'], width=1)
		myFont = ImageFont.truetype(self.arial_bold, self.msgfont_pt)
		draw.fontmode = "1"
		#w, h = draw.textsize("OK", font=myFont)
		left, top, right, bottom = draw.textbbox((0, 0), "OK", font=myFont)
		w, h = right - left, bottom - top
		font_y_offset = top
		draw.text(((66-w)/2,((22-h)-font_y_offset)/2), "OK", fill=colors['buttontext'], font=myFont)
		#button.save("button.png", "PNG")

		# Then we create the window itself
		myFont = ImageFont.truetype(self.arial, self.msgfont_pt)
		#msg_text_w, msg_text_h = draw.textsize("Message Text", font=myFont)
		left, top, right, bottom = draw.textbbox((0, 0), "Message Text", font=myFont)
		msg_text_w, msg_text_h = right - left, bottom - top
		message_box = Image.new('RGB', (173, self.iCaptionHeight+8+msg_text_h+3+button.size[1]+6), color = colors['buttondkshadow']) 
		draw = ImageDraw.Draw(message_box)
		draw.line([(0,0),(171, 0), (0,0), (0,message_box.size[1]-2)],fill=colors['buttonlight'], width=1)
		draw.line([(message_box.size[0]-2,1),(message_box.size[0]-2,message_box.size[1]-2 )],fill=colors['buttonshadow'], width=1)
		draw.line([(1,message_box.size[1]-2),(message_box.size[0]-2,message_box.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.line([(1,1),(message_box.size[0]-3, 1), (1,1),(1, message_box.size[1]-3)],fill=colors['buttonhilight'], width=1)
		draw.rectangle(((2, 2), (message_box.size[0]-3, message_box.size[1]-3)), fill=colors['activeborder'], width=1)
		draw.rectangle(((3, 3), (message_box.size[0]-4, message_box.size[1]-4)), fill=colors['buttonface'], width=1)
		draw.fontmode = "1"
		#font_y_offset = myFont.getoffset("Message Text")[1]
		font_y_offset = self.get_font_y_offset(draw, "Message Text", window_font)
		draw.text((7,self.iCaptionHeight+8-font_y_offset), "Message Text", fill=colors['windowtext'], font=myFont)
		# We then put all the peices together
		message_box.paste(msgboxtitle, (3,3))
		message_box.paste(self.close_button, (173-self.close_button.size[0]-5, 5))
		message_box.paste(button, (int((173-button.size[0])/2), self.iCaptionHeight+8+msg_text_h+3))

		# We do the same for the inactive window, first creating them window
		draw = ImageDraw.Draw(inactive_window)
		draw.line([(0,0),(inactive_window.size[0]-2, 0), (0,0), (0,inactive_window.size[1]-2)],fill=colors['buttonlight'], width=1)
		draw.line([(inactive_window.size[0]-2,1),(inactive_window.size[0]-2,inactive_window.size[1]-2 )],fill=colors['buttonshadow'], width=1)
		draw.line([(1,inactive_window.size[1]-2),(inactive_window.size[0]-2,inactive_window.size[1]-2)],fill=colors['buttonshadow'], width=1)
		draw.line([(1,1),(inactive_window.size[0]-3, 1), (1,1),(1, inactive_window.size[1]-3)],fill=colors['buttonhilight'], width=1)
		draw.rectangle(((2, 2), (inactive_window.size[0]-3, inactive_window.size[1]-3)), fill=colors['activeborder'], width=1)
		draw.rectangle(((3, 3), (inactive_window.size[0]-4, inactive_window.size[1]-4)), fill=colors['buttonface'], width=1)
		#Then putting all the pieces inside
		inactive_window.paste(inactivetitle, (4,4))
		inactive_window.paste(self.close_button, (inactive_window.size[0]-self.close_button.size[0]-6, 6))
		inactive_window.paste(self.max_button, (inactive_window.size[0]-self.close_button.size[0]-6-2-self.max_button.size[0], 6))
		inactive_window.paste(self.min_button, (inactive_window.size[0]-self.close_button.size[0]-6-2-self.max_button.size[0]-self.min_button.size[0], 6))

		height = 39 + (self.iCaptionHeight * 2) + self.iMenuHeight + message_box.size[1]
		width = 4 + activewindow.size[0]

		# Now that we've created all the windows we need, next is to put them all together as one
		demowindows = Image.new('RGBA', (width, height), color = (0, 0, 0, 0)) 
		demowindows.paste(inactive_window)
		demowindows.paste(activewindow, (4,5+self.iCaptionHeight))
		demowindows.paste(message_box, (12,39 + (self.iCaptionHeight * 2) + self.iMenuHeight))

		########
		# ~~~~~~~~~~~~~~~
		########

		# With the windows done we move on to the icons
		# First we make the text under each icon
		# My Computer
		iconfont = ImageFont.truetype(self.lfFont, self.iconfont_pt)
		#size = iconfont.getsize("My Computer")
		left, top, right, bottom = draw.textbbox((0, 0), "My Computer", font=iconfont)
		size = (right - left, bottom - top)
		#font_y_offset = iconfont.getoffset("My Computer")[1]
		font_y_offset = self.get_font_y_offset(draw, "My Computer", iconfont)
		squaresize = (size[0] + 6, size[1] + 6- font_y_offset)
		my_computer_text = Image.new('RGBA', squaresize, colors['background'])
		iconfont_draw = ImageDraw.Draw(my_computer_text)
		iconfont_draw.fontmode = "1"
		iconfont_draw.text((3,3-font_y_offset), "My Computer", fill=colors['foreground'], font=iconfont)
		# Network Neighborhood
		#size = iconfont.getsize("Network Neighborhood")
		left, top, right, bottom = draw.textbbox((0, 0), "Network Neighborhood", font=iconfont)
		size = (right - left, bottom - top)
		# font_y_offset = iconfont.getoffset("Network Neighborhood")[1]
		font_y_offset = self.get_font_y_offset(draw, "Network Neighborhood", iconfont)
		squaresize = (size[0] + 6, size[1] + 6 - font_y_offset)
		network_neighborhood_text = Image.new('RGBA', squaresize, colors['background'])
		iconfont_draw = ImageDraw.Draw(network_neighborhood_text)
		iconfont_draw.fontmode = "1"
		iconfont_draw.text((3,3-font_y_offset), "Network Neighborhood", fill=colors['foreground'],font=iconfont)
		# Recycle Bin
		# size = iconfont.getsize("Recycle Bin")
		left, top, right, bottom = draw.textbbox((0, 0), "Recycle Bin", font=iconfont)
		size = (right - left, bottom - top)
		# font_y_offset = iconfont.getoffset("Recycle Bin")[1]
		font_y_offset = self.get_font_y_offset(draw, "Recycle Bin", iconfont)
		squaresize = (size[0] + 6, size[1] + 6- font_y_offset)
		recycle_bin_empty_text = Image.new('RGBA', squaresize, colors['background'])
		iconfont_draw = ImageDraw.Draw(recycle_bin_empty_text)
		iconfont_draw.fontmode = "1"
		iconfont_draw.text((3,3-font_y_offset), "Recycle Bin", fill=colors['foreground'], font=iconfont)

		# My Documents
		# Not all themes have one
		if self.my_documents:
			# size = iconfont.getsize("My Documents")
			left, top, right, bottom = draw.textbbox((0, 0), "My Documents", font=iconfont)
			size = (right - left, bottom - top)
			# font_y_offset = iconfont.getoffset("My Documents")[1]
			font_y_offset = self.get_font_y_offset(draw, "My Documents", iconfont)
			squaresize = (size[0] + 6, size[1] + 6- font_y_offset)
			my_documents_text = Image.new('RGBA', squaresize, colors['background'])
			iconfont_draw = ImageDraw.Draw(my_documents_text)
			iconfont_draw.fontmode = "1"
			iconfont_draw.text((3,3-font_y_offset), "My Documents", fill=colors['foreground'], font=iconfont)

		# Now we create a canvas to put all the icons and their text on
		total_height = ( self.my_computer.size[1] + 4 + my_computer_text.size[1] + 16 + 
				 self.network_neighborhood.size[1] + 4 + network_neighborhood_text.size[1] + 16 +
				 self.recycle_bin_empty.size[1] + 4 + recycle_bin_empty_text.size[1] )

		if self.my_documents:
			total_height += 16 + self.my_documents.size[1] + 4 + my_documents_text.size[1]
		
		icons = Image.new('RGBA', (network_neighborhood_text.size[0], total_height), color = (0, 0, 0, 0))
		# The center is determined by the longest text
		icon_centerline = int((network_neighborhood_text.size[0]-self.network_neighborhood.size[0])/2)
		# Then we start dropping in Icons/Text
		icons.paste(self.my_computer, (icon_centerline,0), mask=self.my_computer)
		icons.paste(my_computer_text, (int((icons.size[0]-my_computer_text.size[0])/2),self.my_computer.size[1]+4))

		nn_height = self.my_computer.size[1] + 4 + my_computer_text.size[1] + 16
		nn_text_height = self.network_neighborhood.size[1] + nn_height + 4
		icons.paste(self.network_neighborhood, (icon_centerline,nn_height), mask=self.network_neighborhood)
		icons.paste(network_neighborhood_text, (0, nn_text_height))

		rb_height = nn_height + self.network_neighborhood.size[1] + 4 + network_neighborhood_text.size[1] + 16
		rb_text_height = self.recycle_bin_empty.size[1] + rb_height + 4
		icons.paste(self.recycle_bin_empty, (icon_centerline,rb_height), mask=self.recycle_bin_empty)
		icons.paste(recycle_bin_empty_text, (int((network_neighborhood_text.size[0]-recycle_bin_empty_text.size[0])/2),rb_text_height))

		if self.my_documents:
			md_height = rb_height + self.recycle_bin_empty.size[1] + 4 + recycle_bin_empty_text.size[1] + 16
			md_text_height = self.my_documents.size[1] + md_height + 4
			icons.paste(self.my_documents, (icon_centerline,md_height), mask=self.my_documents)
			icons.paste(my_documents_text, (int((network_neighborhood_text.size[0]-my_documents_text.size[0])/2),md_text_height))

		#Finally we create the preview window and set it to the theme background color
		theme = Image.new('RGB', (392, 332), color = colors['background'])
		#Then we add the wallpaper is we need to
		if self.wallpaper:
		#; 0:  The image is centered if TileWallpaper=0 or tiled if TileWallpaper=1
		#; 2:  The image is stretched to fill the screen
		#; 6:  The image is resized to fit the screen while maintaining the aspect 
		#      ratio. (Windows 7 and later)
		#; 10: The image is resized and cropped to fill the screen while maintaining 
		#      the aspect ratio. (Windows 7 and later)

			if self.tile:
				tilew, tileh = self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))).size
				twidth = int(theme.size[0]/tilew) + 1
				theight = int(theme.size[1]/tileh) + 1
				startw = 0
				starth = 0
				for i in range(0,theight):
					for j in range(0,twidth):
						theme.paste(self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))),
							(startw,starth))
						startw = startw + self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))).size[0]
					starth = starth + self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))).size[1]
					startw = 0
			elif self.style == 2:
				theme.paste(self.wallpaper.resize((392,332)))
			else:
				centered_size = self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))).size
				theme.paste(self.wallpaper.resize((int(self.wallpaper.size[0]/2.6),int(self.wallpaper.size[1]/2.3))),
					   (int((theme.size[0]-centered_size[0])/2),int((theme.size[1]-centered_size[1])/2)))
				
						
		theme.paste(icons, (1,35), mask=icons)
		theme.paste(demowindows, (theme.size[0]- demowindows.size[0] - 2, theme.size[1]- demowindows.size[1]-7), mask=demowindows)
		#theme.save(self.theme_name+".png", "PNG")
		
		double = theme.resize((theme.size[0]*2,theme.size[1]*2))
		#double.save(self.theme_name+"_double.png", "PNG")
		self.preview_window = theme
		self.preview_window_double = double
		
		print("OK", end='\n', flush=True)

	def render_html_to_image(self, html_path, output_path, width, height):
		"""Render HTML to image using any available browser."""
		html_abs_path = os.path.abspath(html_path)
		html_url = f"file://{html_abs_path}"
		
		# List of browsers to try, in order of preference
		browsers = [
			{
				'name': 'chromium-browser',
				'args': ['--headless', '--disable-gpu', f'--window-size={width},{height}', f'--screenshot={output_path}', html_url]
			},
			{
				'name': 'google-chrome',
				'args': ['--headless', '--disable-gpu', f'--window-size={width},{height}', f'--screenshot={output_path}', html_url]
			},
			{
				'name': 'firefox',
				'args': ['--headless', f'--screenshot={output_path}', f'--window-size={width},{height}', html_url]
			},
			{
				'name': 'brave-browser',
				'args': ['--headless', '--disable-gpu', f'--window-size={width},{height}', f'--screenshot={output_path}', html_url]
			}
		]
		
		# Try to use wkhtmltoimage first if it exists (original method)
		try:
			subprocess.check_call(['wkhtmltoimage', '--quiet', '--height', str(height), '--width', str(width), html_path, output_path])
			return True
		except (subprocess.SubprocessError, FileNotFoundError):
			pass
		
		# If wkhtmltoimage not available, try browsers
		for browser in browsers:
			try:
				subprocess.check_call([browser['name']] + browser['args'])
				return True
			except (subprocess.SubprocessError, FileNotFoundError):
				continue
		
		# If all browsers fail, try ImageMagick's convert
		try:
			subprocess.check_call(['convert', '-size', f'{width}x{height}', html_url, output_path])
			return True
		except (subprocess.SubprocessError, FileNotFoundError):
			pass
		
		# No rendering method available
		return False

	def get_wallpaper(self):
		print("[MakePreview] Wallpaper...", end=' ', flush=True)
		# WallpaperStyle=2
		#; 0:  The image is centered if TileWallpaper=0 or tiled if TileWallpaper=1
		#; 2:  The image is stretched to fill the screen
		#; 6:  The image is resized to fit the screen while maintaining the aspect 
		#      ratio. (Windows 7 and later)
		#; 10: The image is resized and cropped to fill the screen while maintaining 
		#      the aspect ratio. (Windows 7 and later)
		self.wallpaper = False
		self.tile = False
		if (self.plus.theme_config['wallpaper'] and self.plus.theme_config['wallpaper']['theme_wallpaper'] and 
				'path' in self.plus.theme_config['wallpaper']['theme_wallpaper'] and self.plus.theme_config['wallpaper']['theme_wallpaper']['path']):
			
			if os.path.splitext(self.plus.theme_config['wallpaper']['theme_wallpaper']['path'])[1].lower() in [".html", ".htm"]:
				w = 1024
				h = 768
				if "800" in self.plus.theme_config['wallpaper']['theme_wallpaper']['path'] or "800" in self.plus.theme_name:
					w = 800
					h = 600
				
				temp_file = "temp_html.png"
				
				# Try to render HTML to image using our new function
				success = self.render_html_to_image(
					self.plus.theme_config['wallpaper']['theme_wallpaper']['path'],
					temp_file,
					w,
					h
				)
				
				if success and os.path.exists(temp_file):
					self.wallpaper = Image.open(temp_file).convert('RGBA')
					os.remove(temp_file)
				else:
					print("Warning: Could not render HTML wallpaper. Please install a browser like chromium-browser, firefox, or brave.")
					# Fall back to default handling
					try:
						self.wallpaper = Image.open(self.plus.theme_config['wallpaper']['theme_wallpaper']['path']).convert('RGBA')
					except OSError:
						args = ['convert', '-resize', '32x32', self.plus.theme_config['wallpaper']['theme_wallpaper']['path'], "temp_bmp.png"]
						subprocess.check_call(args)
						self.wallpaper = Image.open("temp_bmp.png").convert('RGBA')
						os.remove("temp_bmp.png")
			else:
				try:
					self.wallpaper = Image.open(self.plus.theme_config['wallpaper']['theme_wallpaper']['path']).convert('RGBA')
				except OSError:
					args = ['convert', '-resize', '32x32', self.plus.theme_config['wallpaper']['theme_wallpaper']['path'], "temp_bmp.png"]
					subprocess.check_call(args)
					self.wallpaper = Image.open("temp_bmp.png").convert('RGBA')
					os.remove("temp_bmp.png")
			
			if self.plus.theme_config['wallpaper']['theme_wallpaper']['tilewallpaper']:
				self.tile = True

			self.style = self.plus.theme_config['wallpaper']['theme_wallpaper']['wallpaperstyle']
		print("OK", end='\n', flush=True)

	def make_icons(self, plus, ico_name):

		icon = share_dir+"/assets/" + ico_name+"~"+".png"

		if plus.theme_config['icons'][ico_name]['type'] in ['dll', 'icl']:
			index = plus.theme_config['icons'][ico_name]['index']
			icon_files = plus.extract_icons_from_dll(plus.theme_config['icons'][ico_name]['path'])
			if icon_files:
				icon_filename, icon_file = plus.get_icons_size_dll(icon_files, index)

				if icon_filename:
					f = open(work_dir+"/tmp_"+icon_filename,"wb")
					f.write(icon_file)
					f.close()
					icon = work_dir+"/tmp_"+icon_filename
				else:
					icon = share_dir+"/assets/" + ico_name+"~"+".png"
		else:
			icon_files = plus.extract_ico(plus.theme_config['icons'][ico_name]['path'])
			
			

			if icon_files == 'bmp':
				icon = plus.theme_config['icons'][ico_name]['path']
			elif icon_files:

				for i in icon_files:
					if i['Width'] == 32:
						icon = "{}[{}]".format(plus.theme_config['icons'][ico_name]['path'], i['ID'])
						break
					else:
						icon = "{}[{}]".format(plus.theme_config['icons'][ico_name]['path'], i['ID'])

		args = ['convert', '-resize', '32x32', icon, ico_name+".png"]
		try:
			subprocess.check_call(args)
			icon_image =  Image.open(ico_name+".png").convert('RGBA')
			os.remove(ico_name+".png")
		except subprocess.CalledProcessError:
			icon_image =  Image.open(share_dir+"/assets/" + ico_name+"~.png").convert('RGBA')
		
		return icon_image



	

class plusGTK:
	def __init__(self, themefile=False, colors=32, overlap=1, 
			squaresize=20, installdir=os.getcwd(), 
			chicago95_cursor_path=c95_packaged_cursor_path,
			chicago95_theme_path=c95_packaged_theme_path,
			chicago95_icons_path=c95_packaged_icons_path,
			loglevel=logging.WARNING,
			logfile='plus.log'):

		
		self.themefile=themefile 
		self.colors=colors
		self.overlap=overlap
		self.squaresize=squaresize
		self.installdir=installdir
		self.chicago95_cursor_path=chicago95_cursor_path
		self.chicago95_theme_path=chicago95_theme_path
		self.chicago95_icons_path=chicago95_icons_path
		self.loglevel=loglevel
		self.logfile=logfile

		# Define signal mappings for builder
		self.handlers = {
		"cancel"        : self.cancel,
		"onDestroy": Gtk.main_quit,
		"theme_chosen": self.open_file,
		"install_screensaver" : self.set_install_screensaver,
		"install_sounds" : self.set_install_sounds,
		"install_cursors" : self.set_install_cursors,
		"install_wallpaper" : self.set_install_wallpaper,
		"install_icons" : self.set_install_icons,
		"install_colors" : self.set_install_colors,
		"install_fonts" : self.set_install_fonts,
		"change"        : self.open_file,
		"warning_ok": self.warning_ok,
		"screen_saver_preview" : self.screen_saver_preview,
		"other_previews" : self.other_previews,
		"show_cursor": self.show_cursor,
		"show_icon": self.show_icon,
		"show_sound": self.show_sound,
		"play_sound": self.play_sound,
		"install" : self.install_accept,
		"install_ok": self.install_ok,
		"preview_closed" : self.preview_closed
		}

		
		# GTK Initialization
		self.builder = builder = Gtk.Builder()
		self.builder.add_from_file(libexec_dir+"/plus.glade")
		self.window = self.builder.get_object("Main")
		self.preview = self.builder.get_object("preview")
		self.builder.connect_signals(self.handlers)
		self.file_chooser = self.builder.get_object("open_theme")
		self.filefilter = self.builder.get_object("Microsoft Theme File")
		self.file_chooser.add_filter(self.filefilter)
		self.install_cursors = True
		self.install_icons = True
		self.install_wallpaper = True
		self.install_sounds = True
		self.install_colors = True
		self.install_fonts = True
		self.install_screensaver = True
		self.theme_selected = False
		if self.themefile:
			self.theme = ChicagoPlus(
				themefile=self.themefile, 
				loglevel=self.loglevel, 
				colors=self.colors, 
				overlap=self.overlap, 
				squaresize=self.squaresize, 
				installdir=self.installdir,
				chicago95_cursor_path=self.chicago95_cursor_path,
				chicago95_theme_path=self.chicago95_theme_path,
				chicago95_icons_path=self.chicago95_icons_path,
				logfile=self.logfile)
			self.preview_image = MakePreview(self.theme)
			self.theme_config = self.theme.theme_config
			theme_name = self.builder.get_object("theme_name")
			preview_theme_name = self.builder.get_object("Preview Theme Name")
			theme_name.set_text(self.preview_image.theme_name)
			preview_theme_name.set_text("Preview of '{}'".format(self.preview_image.theme_name))
			preview = self.preview_image.return_preview()
			self.preview.set_from_file(preview)
			self.theme_selected = True
			self.preview_image.delete_preview()
		self.window.show_all()

	def cancel(self, button):
		Gtk.main_quit()

	def open_file(self, button):
		#image_file = "demo2.png"
		#############################################################
		#self.preview.set_from_file(image_file)
		#############################################################
		#print("Image rendered")
		self.themefile = self.file_chooser.get_filename()
		#print(theme_file)
		self.theme = ChicagoPlus(
			themefile=self.themefile, 
			loglevel=self.loglevel, 
			colors=self.colors, 
			overlap=self.overlap, 
			squaresize=self.squaresize, 
			installdir=self.installdir,
			chicago95_cursor_path=self.chicago95_cursor_path,
			chicago95_theme_path=self.chicago95_theme_path,
			chicago95_icons_path=self.chicago95_icons_path,
			logfile=self.logfile)
		self.preview_image = MakePreview(self.theme)
		self.theme.parse_theme()
		self.theme_config = self.theme.theme_config
		theme_name = self.builder.get_object("theme_name")
		preview_theme_name = self.builder.get_object("Preview Theme Name")
		theme_name.set_text(self.preview_image.theme_name)
		preview_theme_name.set_text("Preview of '{}'".format(self.preview_image.theme_name))
		preview = self.preview_image.return_preview()
		self.preview.set_from_file(preview)
		self.theme_selected = True
		self.preview_image.delete_preview()

	def set_install_screensaver(self, toggle):
		if self.install_screensaver:
			self.install_screensaver = False
		else:
			self.install_screensaver = True

	def set_install_cursors(self, toggle):
		if self.install_cursors:
			self.install_cursors = False
		else:
			self.install_cursors = True

	def set_install_sounds(self, toggle):
		if self.install_sounds:
			self.install_sounds = False
		else:
			self.install_sounds = True

	def set_install_wallpaper(self, toggle):
		if self.install_wallpaper:
			self.install_wallpaper = False
		else:
			self.install_wallpaper = True

	def set_install_icons(self, toggle):
		if self.install_icons:
			self.install_icons = False
		else:
			self.install_icons = True

	def set_install_colors(self, toggle):
		if self.install_colors:
			self.install_colors = False
		else:
			self.install_colors = True

	def set_install_fonts(self, toggle):
		if self.install_fonts:
			self.install_fonts = False
		else:
			self.install_fonts = True


	def screen_saver_preview(self, button):

		if not self.theme_config['screensaver']:
			self.warning_msg("Screen Saver Preview", "{} does not include a screensaver".format(self.theme_config['theme_name']))
			return

		try:
			wine = subprocess.check_output(["which", "wine"]).strip()
		except subprocess.CalledProcessError:
			self.warning_msg("Screen Saver Preview", "Wine is not installed and is required to preview screensavers.")
			return

		args = [wine, self.theme_config['screensaver'], '/s']
		subprocess.check_call(args)

	def in_store(self, store, name):
		for row in store:
			if row[1] == name:
				return True
		return False

	def in_store_location(self, store, name):
		for x in range(len(store)):
			if store[x][1] == name:
				return x
		return 0


	def other_previews(self, button):
		checkmark = GdkPixbuf.Pixbuf.new_from_file(share_dir+"/assets/check.png")
		nocheckmark = GdkPixbuf.Pixbuf.new_from_file(share_dir+"/assets/blank-check.png")
		self.previews_window = self.builder.get_object("Preview Window")
		
		self.cursor_preview = self.builder.get_object("cursor_preview")
		self.cursor_preview.set_from_file(share_dir+"/assets/blank-check.png")

		self.icon_preview = self.builder.get_object("icon_preview")
		self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")

		self.sound_preview = self.builder.get_object("sound_preview")
		self.sound_preview.set_from_file(share_dir+"/assets/blank-check.png")


		self.cursor_preview = self.builder.get_object("cursor_preview")
		self.cursor_preview.set_from_file(share_dir+"/assets/blank-check.png")

		# Populate cursor preview
		self.cursor_store = self.builder.get_object("cursor_list")
		for current_cursor in pointers:
			print("[previews] Generating cursor preview for: {} (name: {})".format(current_cursor, pointers[current_cursor]))
			if (current_cursor not in self.theme_config['cursors'] or not 
			    self.theme_config['cursors'][current_cursor] or not 
			    self.theme_config['cursors'][current_cursor]['path']): 
				if not self.in_store(self.cursor_store, pointers[current_cursor]):
					self.cursor_store.append([nocheckmark,pointers[current_cursor]])
				else:
					loc = self.in_store_location(self.cursor_store, pointers[current_cursor])
					self.cursor_store[loc][0] = nocheckmark
				
			else:
				filename = self.theme_config['cursors'][current_cursor]['path']
				cursor_filename = self.theme_config['cursors'][current_cursor]['filename']
				cursor_type = self.theme_config['cursors'][current_cursor]['type']
				convert_args = ['convert', '-dispose', 'Background']
				if cursor_type == 'ani':
					ani_file_config = self.theme.extract_ani(filename)
					# convert -delay X image1 -delay Y image2 -delay Z image3 -loop 0 animation.gif
					
					if ani_file_config['seq']:
						for sequence in ani_file_config['seq']:
							if ani_file_config['rate']:
								rate = ani_file_config['rate'][sequence] + 5
							else:
								rate = ani_file_config['anih']['iDispRate'] + 5

							for icon in ani_file_config['icon']:
								if icon['index'] == sequence:
									cur_filename = current_cursor+"_"+str(sequence)
									f = open(work_dir+"/"+cur_filename+".cur","wb")
									f.write(icon['ico_file'])
									f.close()
									convert_args.append("-delay")
									convert_args.append("{}x60".format(rate))
									convert_args.append(work_dir+"/"+cur_filename+".cur")
					else:
						for icon in ani_file_config['icon']:
							rate = ani_file_config['anih']['iDispRate'] + 5
							cur_filename = current_cursor+"_"+str(icon['index'])
							f = open(work_dir+"/"+cur_filename+".cur","wb")
							f.write(icon['ico_file'])
							f.close()
							convert_args.append("-delay")
							convert_args.append("{}x60".format(rate))
							convert_args.append(work_dir+"/"+cur_filename+".cur")
					convert_args.append("-loop")
					convert_args.append("0")
					convert_args.append(work_dir+"/"+current_cursor+".gif")
#					pprint(convert_args)
					try:
						subprocess.check_call(convert_args)
					except:
						copyfile(share_dir+"/assets/blank-check.png", work_dir+"/"+current_cursor+".gif")
				else:
					cursor_file_config = self.theme.extract_cur(filename)
					icon_file = cursor_file_config['icon'][0]['ico_file']
					f = open(work_dir+"/"+current_cursor+".cur","wb")
					f.write(icon_file)
					f.close()
					try:
						subprocess.check_call(['convert', work_dir+"/"+current_cursor+".cur", work_dir+"/"+current_cursor+".gif"])
					except:
						copyfile(share_dir+"/assets/blank-check.png", work_dir+"/"+current_cursor+".gif")

				if not self.in_store(self.cursor_store, pointers[current_cursor]):
					self.cursor_store.append([checkmark,pointers[current_cursor]])
				else:
					loc = self.in_store_location(self.cursor_store, pointers[current_cursor])
					self.cursor_store[loc][0] = checkmark

		# Populate Icons
		self.icon_store = self.builder.get_object("icon_list")
		#pprint(self.theme_config)
		#print(self.theme_config['wallpaper'] and self.theme_config['wallpaper']['theme_wallpaper'])
		# Wallpaper
		print("[previews] Getting wallpaper")		
		if self.theme_config['wallpaper'] and self.theme_config['wallpaper']['theme_wallpaper']:
			if not self.in_store(self.icon_store, "Wallpaper bitmap"):
				self.icon_store.append([checkmark,"Wallpaper bitmap"])
			else:
				loc = self.in_store_location(self.icon_store, "Wallpaper bitmap")
				self.icon_store[loc][0] = checkmark
		else:
			if not self.in_store(self.icon_store, "Wallpaper bitmap"):
				self.icon_store.append([nocheckmark,"Wallpaper bitmap"])
			else:
				loc = self.in_store_location(self.icon_store, "Wallpaper bitmap")
				self.icon_store[loc][0] = nocheckmark
		# Icons
		for icon in icons:
			print("[previews] Generating icon preview for: {} (name: {})".format(icon, icons[icon]))
			if not self.theme_config['icons'][icon]:
				if not self.in_store(self.icon_store, icons[icon]):
					self.icon_store.append([nocheckmark,icons[icon]])
				else:
					loc = self.in_store_location(self.icon_store, icons[icon])
					self.icon_store[loc][0] = nocheckmark
			else:
				icon_image = self.preview_image.make_icons(self.theme, icon)
				icon_image.save(work_dir+"/"+icon+".png", "PNG")
				if not self.in_store(self.icon_store, icons[icon]):
					self.icon_store.append([checkmark,icons[icon]])
				else:
					loc = self.in_store_location(self.icon_store, icons[icon])
					self.icon_store[loc][0] = checkmark
		#screensaver
		print("[previews] Getting screensaver")		
		if self.theme_config['screensaver']:
			if not self.in_store(self.icon_store, "Screen saver"):
				self.icon_store.append([checkmark,"Screen saver"])
			else:
				loc = self.in_store_location(self.icon_store, "Screen saver")
				self.icon_store[loc][0] = checkmark
		else:
			if not self.in_store(self.icon_store, "Screen saver"):
				self.icon_store.append([nocheckmark,"Screen saver"])
			else:
				loc = self.in_store_location(self.icon_store, "Screen saver")
				self.icon_store[loc][0] = nocheckmark

		# Sounds
		self.sound_store = self.builder.get_object("sound_list")
		for sound in sounds:
			print("[previews] Generating sound preview for: {} (name: {})".format(sound, sounds[sound]))
			if sound not in self.theme_config['sounds']:
				if not self.in_store(self.sound_store, sounds[sound]):
					self.sound_store.append([nocheckmark,sounds[sound]])
				else:
					loc = self.in_store_location(self.sound_store, sounds[sound])
					self.sound_store[loc][0] = nocheckmark
			else:
				if not self.in_store(self.sound_store, sounds[sound]):
					self.sound_store.append([checkmark,sounds[sound]])
				else:
					loc = self.in_store_location(self.sound_store, sounds[sound])
					self.sound_store[loc][0] = checkmark
		self.sound_path = False
		for sound in sounds:
			if sound in self.theme_config['sounds']:
				self.sound_path = self.theme_config['sounds'][sound]
				break
			
		
		
		self.previews_window.show_all()

	def show_cursor(self,widget, row, col):
		
		self.cursor_text_path = self.builder.get_object("cursor_path")
		model = widget.get_model()
		for cursor in pointers:
			if pointers[cursor] == model[row][1]:
				if cursor in self.theme_config['cursors'] and self.theme_config['cursors'][cursor] is not False:				
					self.cursor_preview.set_from_file(work_dir+"/"+cursor+".gif")
					self.cursor_text_path.set_text(self.theme_config['cursors'][cursor]['path'])
				else:
					self.cursor_preview.set_from_file(share_dir+"/assets/blank-check.png")
					self.cursor_text_path.set_text("")
				break

	def show_icon(self,widget, row, col):
		
		self.icon_text_path = self.builder.get_object("icon_path")
		model = widget.get_model()

		if model[row][1] == "Wallpaper bitmap":
			if self.theme_config['wallpaper'] and self.theme_config['wallpaper']['theme_wallpaper']:
				self.icon_text_path.set_text(self.theme_config['wallpaper']['theme_wallpaper']['path'])
				self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")
			else:
				self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")
				self.icon_text_path.set_text("")
			return
		if model[row][1] == "Screen saver":
			if self.theme_config['screensaver'] :
				self.icon_text_path.set_text(self.theme_config['screensaver'])
				self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")
			else:
				self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")
				self.icon_text_path.set_text("")
			return
		for icon in icons:
			#print(icon, icons[icon], model[row][1])
			if icons[icon] == model[row][1]:
				if self.theme_config['icons'][icon] is not False:				
					self.icon_preview.set_from_file(work_dir+"/"+icon+".png")
					self.icon_text_path.set_text(self.theme_config['icons'][icon]['path'])
				else:
					self.icon_preview.set_from_file(share_dir+"/assets/blank-check.png")
					self.icon_text_path.set_text("")
				break

	def show_sound(self,widget, row, col):
		
		self.sound_text_path = self.builder.get_object("sound_path")
		model = widget.get_model()
		for sound in sounds:
			if sounds[sound] == model[row][1]:
				if sound in self.theme_config['sounds'] and self.theme_config['sounds'][sound]:
					self.sound_path = self.theme_config['sounds'][sound]
					self.sound_text_path.set_text(self.sound_path)
				else:
					self.sound_path = False
					self.sound_text_path.set_text("")


	def play_sound(self, button):
		if self.sound_path:
			#print("Playing {} with aplay".format(self.sound_path))
			try:
				subprocess.check_call(['aplay', self.sound_path])
			except:
				self.warning_msg("Error", "aplay required to play sound previews or sound file corrupt.")


	def preview_closed(self, *args):
		self.previews_window.hide()
		return True

	def warning_msg(self, title="Error", message="Error"):
		self.warning_popup = self.builder.get_object("Warning")
		warning_dialogue = self.builder.get_object("warning_label")
		self.warning_popup.set_title(title)
		warning_dialogue.set_text(message)
		self.warning_popup.show_all()

	def warning_ok(self, *args):
		self.warning_popup.hide()
		return True

	def install_accept(self, button):
		self.install_theme()
		return

	def install_ok(self, button):
		if not self.theme_selected:
			return False
		self.install_theme()
		Gtk.main_quit()

	def install_theme(self):
		if not self.theme_selected:
			return False

		print("Installing theme with the following options:")
		options = "Theme File: {}\nInkscape Options:\n\tColors: {} Overlap: {} Squaresize: {}\nInstall Directory: {}\nPaths:\n\tCursor Path: {}\n\tTheme Path: {}\n\tIcons Path: {}".format(
		self.theme_config['theme_file'], self.colors, self.overlap, self.squaresize,
		self.installdir, self.chicago95_cursor_path, self.chicago95_theme_path,
		self.chicago95_icons_path)

		checks = "Install (checkbox) Options:\n\tCursors: {}\n\tIcons: {}\n\tWallpaper: {}\n\tSounds: {}\n\tColors: {}\n\tFonts: {}\n\tScreensaver: {}".format(
		self.install_cursors, self.install_icons, self.install_wallpaper,
		self.install_sounds, self.install_colors, self.install_fonts, self.install_screensaver)
		print(options)
		print(checks)
		
		self.theme.go(cursors=self.install_cursors, icons=self.install_icons, wallpaper=self.install_wallpaper, 
			      sounds=self.install_sounds, colors=self.install_colors, fonts=self.install_fonts, screensaver=self.install_screensaver)





def main():
	

	desc = '''Chicago95 Plus!'''
	arg_parser = argparse.ArgumentParser(description=desc, 
						usage='%(prog)s [options] [MS Theme File]', 
						epilog="Part of the Chicago95 theme project",
						formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	arg_parser.add_argument('-d', '--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
	arg_parser.add_argument('-c', '--colors', help='How many colors before skipping Inkscape fix/merge for SVGs. Set to 1 to speed up conversion. WARNING: This may result in transparent icons!', default=32, type=int)
	arg_parser.add_argument('-o', '--overlap', help='Pixel overlap for SVG icons', default=1, type=int)	
	arg_parser.add_argument('-s', '--squaresize', help='Square size for SVG icons', default=20, type=int)
	arg_parser.add_argument('--cursorfolder', help="Chicago95 cursor folder to convert to new theme", default=c95_packaged_cursor_path)
	arg_parser.add_argument('--themefolder', help="Chicago95 theme folder to convert to new theme", default=c95_packaged_theme_path)
	arg_parser.add_argument('--iconsfolder', help="Chicago95 icons folder to convert to new theme", default=c95_packaged_icons_path)
	arg_parser.add_argument("--installdir", help="Folder to create new theme in, default is current working directory", default=os.getcwd())
	arg_parser.add_argument("--logfile", help="Filename for debug logging", default="chicago95_plus.log")
	arg_parser.add_argument("theme_file", help="Microsoft Windows 95/98/ME .theme file", nargs="?",default=False)


	args = arg_parser.parse_args()	

	plus = plusGTK(themefile=args.theme_file, 
			   loglevel=args.loglevel, 
			   colors=args.colors, 
			   overlap=args.overlap, 
			   squaresize=args.squaresize, 
			   installdir=args.installdir,
			   chicago95_cursor_path=args.cursorfolder,
			   chicago95_theme_path=args.themefolder,
			   chicago95_icons_path=args.iconsfolder,
			   logfile=args.logfile)


	#plus = plusGTK()
	Gtk.main()	

main()