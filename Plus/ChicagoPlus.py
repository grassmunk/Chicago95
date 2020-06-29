#!/usr/bin/env python3

import sys
from pluslib import ChicagoPlus
import argparse
import logging
import os
from pathlib import Path

def main():
	

	desc = '''Chicago95 Plus! is a python script that can parse Windows 95/98/ME/XP theme files and create new Chicago95 themes. Chicago95 Plus! supports Icons, Cursors, Fonts, Wallpapers, Sounds and Theme colors! Use this against themes you can find on ThemeWorld or any site that have Microsoft Plus! Themes!\nThis script can be called from any folder, execute it and provide it the path to a theme file (e.g. %(prog)s /home/bgates/Wicked/Wicked.theme) and your new theme will be created!'''
	arg_parser = argparse.ArgumentParser(description=desc, 
						usage='%(prog)s [options] MS_Theme_File', 
						epilog="Part of the Chicago95 theme project",
						formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	arg_parser.add_argument('-d', '--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
	arg_parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
	arg_parser.add_argument("--noinstall", help="Do not place folders nor change theme", action="store_true")
	arg_parser.add_argument("--info", help="Prints the json conversion of the theme file", action="store_true")
	arg_parser.add_argument('-c', '--colors', help='How many colors before skipping Inkscape fix/merge for SVGs. Set to 1 to speed up conversion. WARNING: This may result in transparent icons!', default=32, type=int)
	arg_parser.add_argument('-o', '--overlap', help='Pixel overlap for SVG icons', default=1, type=int)	
	arg_parser.add_argument('-s', '--squaresize', help='Square size for SVG icons', default=20, type=int)
	arg_parser.add_argument('--cursorfolder', help="Chicago95 cursor folder to convert to new theme", default=str(Path.home())+"/.icons/Chicago95_Cursor_Black")
	arg_parser.add_argument('--themefolder', help="Chicago95 theme folder to convert to new theme", default=str(Path.home())+"/.themes/Chicago95")
	arg_parser.add_argument('--iconsfolder', help="Chicago95 icons folder to convert to new theme", default=str(Path.home())+"/.icons/Chicago95")
	arg_parser.add_argument("--installdir", help="Folder to create new theme in, default is current working directory", default=os.getcwd())
	arg_parser.add_argument("--logfile", help="Filename for debug logging", default="chicago95_plus.log")
	arg_parser.add_argument("theme_file", help="Microsoft Windows 95/98/ME .theme file")
	specific_args = arg_parser.add_argument_group("Specific Installs")
	specific_args.add_argument("--nocursors", help="Do not generate/install/enable the cursors", action="store_false")
	specific_args.add_argument("--noicons", help="Do not generate/install/enable the icons", action="store_false")
	specific_args.add_argument("--nowallpaper", help="Do not generate/install/enable the wallpaper", action="store_false")
	specific_args.add_argument("--nosounds", help="Do not generate/install/enable the sounds", action="store_false")
	specific_args.add_argument("--nocolors", help="Do not generate/install/enable the colors", action="store_false")
	specific_args.add_argument("--nofonts", help="Do not generate/install/enable the fonts", action="store_false")
	specific_args.add_argument("--noscreensaver", help="Do not generate/install the screensaver", action="store_false")

	args = arg_parser.parse_args()	

	plus = ChicagoPlus(themefile=args.theme_file, 
			   loglevel=args.loglevel, 
			   colors=args.colors, 
			   overlap=args.overlap, 
			   squaresize=args.squaresize, 
			   installdir=args.installdir,
			   chicago95_cursor_path=args.cursorfolder,
			   chicago95_theme_path=args.themefolder,
			   chicago95_icons_path=args.iconsfolder,
			   logfile=args.logfile)

	print(plus.logo())

	if args.info:
		plus.parse_theme()
		plus.print_theme_config()
		sys.exit(0)

	if args.noinstall:
		plus.check_software(args.nocursors, args.noicons, args.colors)
		plus.parse_theme()
		plus.generate_theme(cursors=args.nocursors, icons=args.noicons, wallpaper=args.nowallpaper, sounds=args.nosounds, colors=args.nocolors, fonts=args.nofonts, screensaver=args.noscreensaver)
	else:
		plus.go(cursors=args.nocursors, icons=args.noicons, wallpaper=args.nowallpaper, sounds=args.nosounds, colors=args.nocolors, fonts=args.nofonts, screensaver=args.noscreensaver)	

main()
