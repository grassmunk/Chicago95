#!/usr/bin/env python3
import struct
# Xcursors Original mapping based on https://revadig.blogspot.com/2017/09/x11-xorg-set-mouse-pointer-cursor.html
# Hashes/Extras: https://fedoraproject.org/wiki/Artwork/EchoCursors/NamingSpec
# QT Cursor names: https://doc.qt.io/archives/qtjambi-4.5.2_01/com/trolltech/qt/gui/QCursor.html
# GDK Cursor: https://developer.gnome.org/gdk3/stable/gdk3-Cursors.html
# Freedesktop cursors (fd): https://www.freedesktop.org/wiki/Specifications/cursor-spec/
import subprocess
import os
import shutil
import sys

# If you're parsing Microsoft Windows 95 default animated cursors, pass the '-s' argument to skip the ugly first frame

cursors = {
'X_cursor': {'Windows Default': False,
                  'fd': [],
                  'gdk': [],
                  'hashes': ['X-cursor'],
                  'name': 'Cursor Logo',
                  'qt': [],
                  'xcursors': ['X_cursor',
                               'boat',
                               'pirate',
                               'sailboat',
                               'shuttle',
                               'spider, trek',
                               'umbrella',
                               'coffee_mug']},
 'appstarting': {'Windows Default': True,
                     'fd': ['progress'],
                     'gdk': ['progress'],
                     'hashes': ['08e8e1c95fe2fc01f976f1e063a24ccd',
                                '3ecb610c1bf2410f44200f48c40d3599', '00000000000000020006000e7e9ffc3f'],
                     'name': 'Working in Background',
                     'qt': ['left_ptr_watch', 'half-busy'],
                     'xcursors': []},
 'arrow': {'Windows Default': True,
               'fd': ['default'],
               'gdk': ['default'],
               'hashes': ['top-left-arrow'],
               'name': 'Normal Select',
               'qt': ['left_ptr'],
               'xcursors': ['arrow',
                            'draft_large',
                            'draft_small',
                            'left_ptr',
                            'top_left_arrow']},
 'bottom_tee': {'Windows Default': False,
                    'fd': [],
                    'gdk': [],
                    'hashes': ['bottom_tee'],
                    'name': 'Cell select bottom(?)',
                    'qt': [],
                    'xcursors': ['bottom_tee']},
 'circle': {'Windows Default': False,
                'fd': [],
                'gdk': [],
                'hashes': [],
                'name': 'Circle? Bullseye?',
                'qt': [],
                'xcursors': ['circle', 'target']},
 'clock': {'Windows Default': False,
               'fd': [],
               'gdk': [],
               'hashes': [],
               'name': 'Clock? Not used?',
               'qt': [],
               'xcursors': ['clock']},
 'copy': {'Windows Default': False,
              'fd': ['copy'],
              'gdk': ['copy', 'grab', 'grabbing'],
              'hashes': ['dnd-copy',
                         '1081e37283d90000800003c07f3ef6bf',
                         '6407b0e94181790501fd1e167b474872',
                         '08ffe1cb5fe6fc01f906f1c063814ccf',
                         '5aca4d189052212118709018842178c0',
                         '208530c400c041818281048008011002',
                         'fcf21c00b30f7e3f83fe0dfd12e71cff'],
              'name': 'Drag and drop copy',
              'qt': [],
              'xcursors': []},
 'cross': {'Windows Default': False,
               'fd': [],
               'gdk': [],
               'hashes': [],
               'name': 'Crosshair',
               'qt': [],
               'xcursors': ['crosshair', 'cross_reverse']},
 'crosshair': {'Windows Default': True,
                   'fd': ['crosshair'],
                   'gdk': ['crosshair'],
                   'hashes': [],
                   'name': 'Precision select',
                   'qt': ['cross'],
                   'xcursors': ['cross',
                                'diamond_cross',
                                'iron_cross',
                                'tcross']},
 'dotbox': {'Windows Default': False,
                'fd': [],
                'gdk': [],
                'hashes': ['dot-box', 'dot_box', 'dot_box_mask'],
                'name': 'dot in a box(?)',
                'qt': [],
                'xcursors': ['dotbox',
                             'dot',
                             'bogosity',
                             'box_spiral',
                             'draped_box',
                             'heart, icon',
                             'rtl_logo']},
 'exchange': {'Windows Default': False,
                  'fd': [],
                  'gdk': [],
                  'hashes': [],
                  'name': 'Clock? Not used?',
                  'qt': [],
                  'xcursors': ['exchange']},
 'gumby': {'Windows Default': False,
               'fd': [],
               'gdk': [],
               'hashes': [],
               'name': 'Fun characters',
               'qt': [],
               'xcursors': ['gumby', 'gobbler', 'man']},
 'hand1': {'Windows Default': False,
               'fd': ['pointer'],
               'gdk': ['pointer'],
               'hashes': ['9d800788f1b08800ae810202380a0822',
                          'e29285e634086352946a0e7090d73106',
                          'hand', 'HandGrab', 'HandSqueezed'],
               'name': 'Hand pointer',
               'qt': ['pointing_hand', 'openhand'],
               'xcursors': ['hand1', 'hand2']},
 'help': {'Windows Default': True,
              'fd': ['help', 'context-menu'],
              'gdk': ['help', 'context-menu'],
              'hashes': ['ask', 'dnd-ask', 'd9ce0ab605698f320427677b458ad60b',
                                           '5c6cd98b3f3ebcb1f9c7f1c204630408'],
              'name': 'Help Select',
              'qt': ['whats_this'],
              'xcursors': ['question_arrow']},
 'ibeam': {'Windows Default': True,
               'fd': ['text'],
               'gdk': ['text'],
               'hashes': [],
               'name': 'Text Select',
               'qt': ['ibeam'],
               'xcursors': ['xterm']},
 'left_tee': {'Windows Default': False,
                  'fd': [],
                  'gdk': [],
                  'hashes': ['left_tee'],
                  'name': 'Cell select bottom(?)',
                  'qt': [],
                  'xcursors': ['left_tee']},
 'link': {'Windows Default': False,
              'fd': ['link'],
              'gdk': ['alias'],
              'hashes': ['3085a0e285430894940527032f8b26df',
                         '640fb0e74195791501fd1ed57b41487f',
                         'a2a266d0498c3104214a47bd64ab0fc8',
                         '0876e1c15ff2fc01f906f1c363074c0f', 'dnd-link'],
              'name': 'Create link',
              'qt': ['closedhand'],
              'xcursors': []},
 'mouse': {'Windows Default': False,
               'fd': [],
               'gdk': [],
               'hashes': [],
               'name': 'Mouse demo',
               'qt': [],
               'xcursors': ['mouse', 'middlebutton', 'rightbutton']},
 'move': {'Windows Default': False,
              'fd': [],
              'gdk': [],
              'hashes': ['move',
                         'dnd-move',
                         '4498f0e0c1937ffe01fd06f973665830',
                         '9081237383d90e509aa00f00170e968f'],
              'name': 'color picker',
              'qt': [],
              'xcursors': []},
 'no': {'Windows Default': True,
            'fd': ['no-drop', 'not-allowed'],
            'gdk': ['no-drop', 'not-allowed'],
            'hashes': ['dnd-none',
                       '03b6e0fcb3499374a867c041f52298f0',
                       'crossed_circle'],
            'name': 'Unavailable/Forbidden',
            'qt': ['forbidden', 'dnd-no-drop'],
            'xcursors': []},
 'pen': {'Windows Default': True,
             'fd': [],
             'gdk': [],
             'hashes': [],
             'name': 'Handwriting',
             'qt': [],
             'xcursors': ['pencil']},
 'picker': {'Windows Default': False,
                'fd': [],
                'gdk': [],
                'hashes': ['picker'],
                'name': 'color picker',
                'qt': ['color-picker'],
                'xcursors': []},
 'plus': {'Windows Default': False,
              'fd': ['cell'],
              'gdk': ['cell'],
              'hashes': [],
              'name': 'Add a cell',
              'qt': [],
              'xcursors': ['plus']},
 'right_ptr': {'Windows Default': False,
                   'fd': [],
                   'gdk': [],
                   'hashes': [],
                   'name': 'Right pointer',
                   'qt': [],
                   'xcursors': ['right_ptr']},
 'right_tee': {'Windows Default': False,
                   'fd': [],
                   'gdk': [],
                   'hashes': ['right_tee'],
                   'name': 'Cell select right(?)',
                   'qt': [],
                   'xcursors': ['right_tee']},
 'sb_h_double_arrow': {'Windows Default': False,
                           'fd': [],
                           'gdk': [],
                           'hashes': ['14fef782d02440884392942c11205230',
                                      'h_double_arrow', '028006030e0e7ebffc7f7070c0600140',
                                      'right', 'HDoubleArrow'],
                           'name': 'Resize area between panels',
                           'qt': ['split_h'],
                           'xcursors': ['sb_h_double_arrow',
                                        'sb_left_arrow',
                                        'sb_right_arrow']},
 'sb_v_double_arrow': {'Windows Default': False,
                           'fd': [],
                           'gdk': [],
                           'hashes': ['2870a09082c103050810ffdffffe0204',
                                      'v_double_arrow', 'VDoubleArrow'],
                           'name': 'Resize area between panels',
                           'qt': ['split_v'],
                           'xcursors': ['sb_v_double_arrow',
                                        'sb_up_arrow',
                                        'sb_down_arrow']},
 'sizeall': {'Windows Default': True,
                 'fd': ['all-scroll'],
                 'gdk': ['move', 'all-scroll'],
                 'hashes': [],
                 'name': 'Move',
                 'qt': ['size_all'],
                 'xcursors': ['fleur']},
 'sizenesw': {'Windows Default': True,
                  'fd': ['ne-resize', 'sw-resize', 'nesw-resize'],
                  'gdk': ['ne-resize', 'sw-resize', 'nesw-resize'],
                  'hashes': ['bd_double_arrow',
                             'fcf1c3c7cd4491d801f1e1c78f100000'],
                  'name': 'Diagonal resize 2',
                  'qt': ['size_bdiag'],
                  'xcursors': ['bottom_left_corner',
                               'll_angle',
                               'top_right_corner',
                               'ur_angle']},
 'sizens': {'Windows Default': True,
                'fd': ['row-resize', 'n-resize', 's-resize', 'ns-resize'],
                'gdk': ['row-resize', 'n-resize', 's-resize', 'ns-resize'],
                'hashes': ['base_arrow_down',
                           'base_arrow_up',
                           'v_double_arrow',
                           '00008160000006810000408080010102'],
                'name': 'Vertical resize',
                'qt': ['size_ver'],
                'xcursors': ['based_arrow_down',
                             'based_arrow_up',
                             'double_arrow',
                             'bottom_side',
                             'top_side']},
 'sizenwse': {'Windows Default': True,
                  'fd': ['nw-resize', 'se-resize', 'nwse-resize'],
                  'gdk': ['nw-resize', 'se-resize', 'nwse-resize'],
                  'hashes': ['fd_double_arrow',
                             'c7088f0f3e6c8088236ef8e1e3e70000'],
                  'name': 'Diagonal resize 1',
                  'qt': ['size_fdiag'],
                  'xcursors': ['top_left_corner',
                               'ul_angle',
                               'lr_angle',
                               'bottom_right_corner',
                               'sizing']},
 'sizewe': {'Windows Default': True,
                'fd': ['col-resize', 'e-resize', 'w-resize', 'ew-resize'],
                'gdk': ['col-resize', 'e-resize', 'w-resize', 'ew-resize'],
                'hashes': [],
                'name': 'Horizontal resize',
                'qt': ['size_hor'],
                'xcursors': ['left_side', 'right_side']},
 'spraycan': {'Windows Default': False,
                  'fd': [],
                  'gdk': [],
                  'hashes': [],
                  'name': 'Grafiti time',
                  'qt': [],
                  'xcursors': ['spraycan']},
 'star': {'Windows Default': False,
              'fd': [],
              'gdk': [],
              'hashes': [],
              'name': 'Star time',
              'qt': [],
              'xcursors': ['star']},
 'top_tee': {'Windows Default': False,
                 'fd': [],
                 'gdk': [],
                 'hashes': ['top_tee'],
                 'name': 'Cell select top(?)',
                 'qt': [],
                 'xcursors': ['top_tee']},
 'uparrow': {'Windows Default': True,
                 'fd': ['up-arrow'],
                 'gdk': [],
                 'hashes': ['basic-arrow', 'bassic_arrow'],
                 'name': 'Alternate Select',
                 'qt': ['up_arrow'],
                 'xcursors': ['center_ptr']},
 'vertical-text': {'Windows Default': False,
                       'fd': ['vertical-text'],
                       'gdk': ['vertical-text'],
                       'hashes': [],
                       'name': 'Vertical text selector',
                       'qt': [],
                       'xcursors': []},
 'wait': {'Windows Default': True,
              'fd': ['wait'],
              'gdk': ['wait'],
              'hashes': [],
              'name': 'Busy',
              'qt': ['wait'],
              'xcursors': ['watch']},
 'zoom-in': {'Windows Default': False,
                 'fd': [],
                 'gdk': ['zoom-in'],
                 'hashes': ['f41c0e382c94c0958e07017e42b00462', 'zoomIn'],
                 'name': 'Zoom in',
                 'qt': [],
                 'xcursors': []},
 'zoom-out': {'Windows Default': False,
                  'fd': [],
                  'gdk': ['zoom-out'],
                  'hashes': ['f41c0e382c97c0938e07017e42800402', 'zoomOut',
                             'a2a266d0498c3104214a47bd64ab0fc8'],
                  'name': 'Drag and drop copy',
                  'qt': [],
                  'xcursors': []}
}

		

def extract_cur(file_name):
	print("\tParsing cursor file {}".format(file_name)) 
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

def convert_cur_files(cursor_filename, output_file_name):
	print("\tConverting {} to {}".format(cursor_filename, output_file_name))
	convert_path = subprocess.check_output(["which", "convert"]).strip()
	args = [
	convert_path,
	cursor_filename,
	output_file_name
	]
	subprocess.check_call(args)
	if  os.path.isfile(output_file_name[:-4]+"-0.png"):
		shutil.move(output_file_name[:-4]+"-1.png", output_file_name[:-4]+".png")
		os.remove(output_file_name[:-4]+"-0.png")
	

def extract_ani(file_name):
	print("\tParsing ani file {}".format(file_name))
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
	print("{:<21} | Extracting cursors/icons from ani file: {}".format("", file_name))

	# ANI files are just RIFF files
	if ckID == 'RIFF':
		print("{:<21} | {} ckSize :{}".format("","RIFF detected", ckSize))
		if ckForm == 'ACON': #ACON is optional
			#print("ACON detected (optional)")
			total_size = 12 # RIFF Header with ACON
		else:
			total_size = 8 # RIFF Header without ACON

		if ckSize == len(ani_bytes) - 8:
			ckSize = ckSize + 8 # Sometimes, but not always, the header isn't included in ckSize
			print("{:<21} | Adjusting ckSize to actual file size: {}".format("",ckSize))

		while total_size < ckSize:
			section = ani_bytes[total_size:total_size+4].decode()
			total_size = total_size + 4
			chunk_size = struct.unpack('<L',ani_bytes[total_size:total_size+4])[0]
			total_size = total_size + 4

			#print("Chunk {}, Size: {}".format(section, chunk_size))
			#print(ani_bytes[total_size:total_size+36])
			if section == 'anih': #ANI Header
				print("{:<21} | Chunk: anih".format(""))
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
				print("{:<21} | Chunk: rate, size: {}".format("", chunk_size))
				rate = []
				for jiffie in range(0,chunk_size,4):
					rate.append(struct.unpack('<L',ani_bytes[total_size+jiffie:total_size+jiffie+4])[0])
			elif section == 'seq ':
				print("{:<21} | Chunk: seq, size: {}".format("",chunk_size))
				seq = []
				for sequence in range(0,chunk_size,4):
					seq.append(struct.unpack('<L',ani_bytes[total_size+sequence:total_size+sequence+4])[0])
				# bfAttributes: 1 == CUR or ICO, 0 == BMP, 3 == 'seq' block is present
			elif section == 'LIST':
				chunk_type = ani_bytes[total_size:total_size+4].decode()
				LIST_item_size = total_size + 4
				print("{:<21} | Chunk: {}, size: {}".format("",chunk_type, chunk_size))
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
						print("{:<21} | Chunk: {}, size: {}".format("",info_section, LIST_item_size))
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
		print("No RIFF ID, is {} an ANI file?".format(file_name))
		print("{:<21} | RIFF ID: {}, Form: {}".format("", ckID, ckForm))


	if INFO:
		for i in INFO:
			print("{:<21} | {:<21} | {}".format("",i, INFO[i]))
	if anih: 
		for i in anih:
			print("{:<21} | {:<21} | {}".format("",i, anih[i]))
	for section in icon:
			if section['index']:
				print("{:<21} | Index: {}".format("",section['index']))
				print("{:<21} | rtIconDir".format(""))
				for j in section['rtIconDir']:
					print("{:<21} | {:<21} | {}".format("",j, section['rtIconDir'][j]))
				print("{:<21} | rtIconDirEntry".format(""))
				for j in section['rtIconDirEntry']:
					print("{:<21} | {:<21} | {}".format("",j, section['rtIconDirEntry'][j]))

	cursor = {
		'INFO' : INFO,
		'anih' : anih,
		'seq'  : seq,
		'rate' : rate,
		'icon' : icon 
	}

	return cursor


if os.path.exists('tmp'):
	shutil.rmtree('tmp')

os.makedirs('tmp')

for cursor in cursors:
	folder = 'xcursors'

	print("Cursor: {}\n\tDesc: {}".format(cursor,cursors[cursor]['name']))

	if cursors[cursor]['Windows Default']:
		folder = '95'

	if os.path.exists("{}/{}.cur".format(folder,cursor)):
		ext = ".cur"
	elif os.path.exists("{}/{}.ani".format(folder,cursor)):
		ext = ".ani"
	elif os.path.exists("{}/{}.ico".format(folder,cursor)):
		ext = ".ico"
	else:
		print("{icon}.cur/{icon}.ani/{icon}.ico could not be found. Please place one of {icon}.cur/{icon}.ani/{icon}.ico in {folder}".format(icon=cursor,folder=folder))
	
	if ext in ['.ico', '.cur']:
		cursor_file_config = extract_cur(folder+"/"+cursor+ext)
		xhot = cursor_file_config['icon'][0]['rtIconDirEntry']['wPlanes']
		yhot = cursor_file_config['icon'][0]['rtIconDirEntry']['wBitCount']
		size = cursor_file_config['icon'][0]['rtIconDirEntry']['bHeight']
		icon_file = cursor_file_config['icon'][0]['ico_file']
		f = open("tmp/"+cursor+ext,"wb")
		f.write(icon_file)
		f.close()

		convert_cur_files("tmp/"+cursor+ext, "tmp/"+cursor+".png")
		write_conf = open("tmp/"+cursor+".conf", 'w')
		print("\tWritting conf file {}: {size} {xhot} {yhot} {filename}".format("tmp/"+cursor+".conf", size=size, xhot=xhot, yhot=yhot, filename=cursor+".png"))
		write_conf.write("{size} {xhot} {yhot} {filename}".format(size=size, xhot=xhot, yhot=yhot, filename=cursor+".png"))
		write_conf.close()
		os.remove("tmp/"+cursor+ext)

	elif ext == '.ani':
		ani_file_config = extract_ani(folder+"/"+cursor+ext)
		#pprint(ani_file_config)
		print("{:<21} | Header - nFrames: {}, nSteps: {}, iDispRate: {}".format(cursor+ext, ani_file_config['anih']['nFrames'], ani_file_config['anih']['nSteps'], ani_file_config['anih']['iDispRate']))
		write_conf = open("tmp/"+cursor+".conf", 'w')

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
						print("{:<21} | Sequence: {}, rate: {}, size: {}, xhot: {}, yhot: {}".format(cursor+ext, sequence, rate, size,xhot, yhot))
						cur_filename = cursor+"_"+str(sequence)
						f = open("tmp/"+cur_filename+".cur","wb")
						f.write(icon['ico_file'])
						f.close()
						convert_cur_files("tmp/"+cur_filename+".cur", "tmp/"+cur_filename+".png")
						write_conf.write("{size} {xhot} {yhot} {filename} {rate}\n".format(size=size, xhot=xhot, yhot=yhot, filename=cur_filename+".png", rate=rate ))
		else:
			itericons = iter(ani_file_config['icon'])			
			# This is just for the default windows icons, no idea why
			if len(sys.argv) > 1 and sys.argv[1] == '-s':
				next(itericons)
			for icon in itericons:
				xhot = icon['rtIconDirEntry']['wPlanes']
				yhot = icon['rtIconDirEntry']['wBitCount']
				size = icon['rtIconDirEntry']['bHeight']
				rate = ani_file_config['anih']['iDispRate'] * 17
				print("{:<21} |  Sequence: {}, rate: {}, size: {}, xhot: {}, yhot: {}".format(cursor+ext, icon['index'], rate, size,xhot, yhot))
				cur_filename = cursor+"_"+str(icon['index'])
				f = open("tmp/"+cur_filename+".cur","wb")
				f.write(icon['ico_file'])
				f.close()
				convert_cur_files("tmp/"+cur_filename+".cur", "tmp/"+cur_filename+".png")
				write_conf.write("{size} {xhot} {yhot} {filename} {rate}\n".format(size=size, xhot=xhot, yhot=yhot, filename=cur_filename+".png", rate=rate))
		
		for icon in ani_file_config['icon']:
			xhot = icon['rtIconDirEntry']['wPlanes']
			yhot = icon['rtIconDirEntry']['wBitCount']
			size = icon['rtIconDirEntry']['bHeight']
			#print(xhot, yhot, size)
		write_conf.close()

	print("\tConversion complete\n\tBuilding xcusorfiles in ../cursors")
	for linux_type in ['xcursors', 'qt', 'fd', 'gdk', 'hashes']:
		for output in cursors[cursor][linux_type]:
			print("\t\t{}".format(output))
			xcursorgen_path = subprocess.check_output(["which", "xcursorgen"]).strip()
			args = [
				xcursorgen_path,
				"-p",
				'tmp',
				"tmp/"+cursor+".conf",
				"../cursors/"+output
			]
			subprocess.check_call(args, stdout=subprocess.DEVNULL)
shutil.rmtree('tmp')
	

