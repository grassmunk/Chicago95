#!/usr/bin/env python3

import gi
import gc
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import os
import subprocess
import time

from pathlib import Path
import shutil


UI_FILE = "installer.glade"

running_folder = os.path.dirname(os.path.abspath(__file__))

assets = "/Extras/"

#HOME_FOLDER = '/home/phil/Chicago95/Cursors/' 


class InstallGUI:
	def __init__(self):
		self.set_style()
		self.builder = Gtk.Builder()
		self.builder.add_from_file(running_folder + assets + UI_FILE)
		self.builder.connect_signals(self)
		self.get_sizes()
		self.set_options()
		window = self.builder.get_object('main window')
		#window.connect('delete-event', lambda x,y: Gtk.main_quit())
		self.window_installer = self.builder.get_object('installer')
		self.window_installer.connect('delete-event', lambda x,y: Gtk.main_quit())
		self.progress_window = self.builder.get_object('progress')
		self.progress_window.connect('delete-event', lambda x,y: Gtk.main_quit())
		window.show_all()
		self.window_installer.show_all()
		print("Installer running from: " + running_folder)

	def set_style(self):
		# From https://gist.github.com/carlos-jenkins/8923124
		provider = Gtk.CssProvider()
		provider.load_from_path(running_folder + "/Theme/Chicago95/gtk-3.0/gtk.css")
		screen = Gdk.Display.get_default_screen(Gdk.Display.get_default())
		# I was unable to found instrospected version of this
		GTK_STYLE_PROVIDER_PRIORITY_APPLICATION = 600
		Gtk.StyleContext.add_provider_for_screen( screen, provider, GTK_STYLE_PROVIDER_PRIORITY_APPLICATION )

	def on_window_destroy(self, window):
		print("Closing Window")
		Gtk.main_quit()
		return False

	def folder_size(self, path='.'):
		return int(subprocess.check_output(['du','-sk', path]).split()[0].decode('utf-8'))

	def get_sizes(self):
			# Get sizes
			statvfs = os.statvfs(running_folder)
			statvfs.f_frsize * statvfs.f_blocks     # Size of filesystem in bytes
			statvfs.f_frsize * statvfs.f_bfree      # Actual number of free bytes
			self.available_kb = (statvfs.f_frsize * statvfs.f_bavail) / 1024
			self.theme_size_kb = self.folder_size(running_folder+"/Theme")
			self.icons_size_kb = self.folder_size(running_folder+"/Icons/Chicago95")
			self.cursors_size_kb = self.folder_size(running_folder+"/Cursors")
			self.background_size_kb = 0
			self.sounds_size_kb = self.folder_size(running_folder+"/sounds")
			self.fonts_size_kb = self.folder_size(running_folder+"/Fonts")
			self.total_size_kb = (self.theme_size_kb + self.icons_size_kb + self.cursors_size_kb + 
						self.background_size_kb + self.sounds_size_kb + self.fonts_size_kb)
	def set_options(self):
		self.install_theme = True
		self.install_icons = True
		self.install_cursors = True
		self.install_background = True
		self.install_sounds = True
		self.install_fonts = True
		self.thunar = True
		self.terminal_colors = True
		self.bash = True
		self.zsh = False
		self.panel = True

	def next_clicked(self, button):
		stack = self.builder.get_object('stack')
		current_page = stack.get_visible_child_name()
		next_button = self.builder.get_object('next')
		if next_button.get_label() == "Install":
			self.install_chicago95()
			return
		
		if next_button.get_label() == "Finish":
			print("Install Completed! Enjoy Chicago95!")
			Gtk.main_quit()
			return False

		if current_page == 'page_welcome':
			#component_page = self.builder.get_object('page_components')
			component_page = stack.get_child_by_name('page_components')
			back_button = self.builder.get_object('back')
			back_button.set_sensitive(True)

			# Get the labels
			self.theme_size = self.builder.get_object('theme size')
			self.icons_size = self.builder.get_object('icons size')
			self.cursors_size = self.builder.get_object('cursors size')
			self.background_size = self.builder.get_object('background size')
			self.sounds_size = self.builder.get_object('sound size')
			self.fonts_size = self.builder.get_object('font size')
			self.remaining_size = self.builder.get_object('remaining size')
			self.total_size = self.builder.get_object('total size')
			# Change the labels
			self.theme_size.set_label("{} k".format(self.theme_size_kb))
			self.icons_size.set_label("{} k".format(self.icons_size_kb))
			self.cursors_size.set_label("{} k".format(self.cursors_size_kb))
			self.sounds_size.set_label("{} k".format(self.sounds_size_kb))
			self.fonts_size.set_label("{} k".format(self.fonts_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))


		else:
			component_page = stack.get_child_by_name('page_customizations')
			thunar_check = self.builder.get_object('thunar')
			panel_check = self.builder.get_object('panel')
			if not self.install_theme:
				print('[THUNAR] Warning: GTK Theme not selected, cannot install Thunar status bar image')
				thunar_check.set_tooltip_text("Warning: GTK Theme not selected, cannot install Thunar status bar image")
				thunar_check.set_sensitive(False)
				thunar_check.set_active(False)
				self.thunar = False
			else:
				thunar_check.set_tooltip_text("Enables the Thunar status bar image")
				thunar_check.set_sensitive(True)
				thunar_check.set_active(True)
				self.thunar = True

			if not self.check_xfce_panel():
				print("[PANEL] Warning: xfce4-panel-profiles not installed, manual panel installation required. See INSTALL.md")
				panel_check.set_tooltip_text("Warning: xfce4-panel-profiles not installed, manual panel installation required. See INSTALL.md")
				panel_check.set_sensitive(False)
				panel_check.set_active(False)
				self.panel = False
				
			next_button.set_label("Install")
			
		stack.set_visible_child(component_page)

	def back_clicked(self, button):
		stack = self.builder.get_object('stack')
		current_page = stack.get_visible_child_name()

		if current_page == 'page_components':
			#component_page = self.builder.get_object('page_components')
			component_page = stack.get_child_by_name('page_welcome')
			back_button = self.builder.get_object('back')
			back_button.set_sensitive(False)

		else:
			component_page = stack.get_child_by_name('page_components')
			next_button = self.builder.get_object('next')
			next_button.set_label("Next")
			
		stack.set_visible_child(component_page)

	def install_chicago95(self):
		components = "\tTheme:\t\t{}\n\tIcons:\t\t{}\n\tCursors:\t{}\n\tBackground:\t{}\n\tSounds:\t\t{}\n\tFonts:\t\t{}".format(self.install_theme, self.install_icons, self.install_cursors, self.install_background, self.install_sounds, self.install_fonts)
		customizations = "\tThunar Graphics:\t{}\n\tChange Terminal Colors:\t{}\n\tSet Bash Prompt:\t{}\n\tSet zsh promt/theme:\t{}\n\tCustomize Panel:\t{}".format(self.thunar, self.terminal_colors, self.bash, self.zsh, self.panel)
		self.progress_label_sections = []
		print("Installing Chicago 95 with the following options:\n Components:\n {}\n Customizations:\n {}".format(components, customizations))
		self.copy_files = {}
		if self.install_theme:
			# Does ~/.themes exist?
			Path(os.path.expanduser("~/.themes")).mkdir(parents=True, exist_ok=True)
			self.copy_files.update(self.get_files(running_folder+"/Theme/Chicago95/", os.path.expanduser("~/.themes"), "Theme"))
			self.copy_files["install_theme"] = self.install_theme
			self.progress_label_sections.append("GTK Theme")
		if self.install_icons:
			Path(os.path.expanduser("~/.icons")).mkdir(parents=True, exist_ok=True)
			self.copy_files.update(self.get_files(running_folder+"/Icons/Chicago95/", os.path.expanduser("~/.icons"), "Icons"))
			self.copy_files["install_icons"] = self.install_icons
			self.progress_label_sections.append("Icons")
		if self.install_cursors:
			Path(os.path.expanduser("~/.icons")).mkdir(parents=True, exist_ok=True)
			self.copy_files.update(self.get_files(running_folder+"/Cursors/", os.path.expanduser("~/.icons"), "Cursors"))
			self.copy_files["install_cursors"] = self.install_cursors
			self.progress_label_sections.append("Cursors")
		if self.install_background:
			self.copy_files["install_background"] = self.install_background
			self.progress_label_sections.append("Background")
		if self.install_sounds:
			Path(os.path.expanduser("~/.local/share/sounds")).mkdir(parents=True, exist_ok=True)
			self.copy_files.update(self.get_files(running_folder+"/sounds/Chicago95/", os.path.expanduser("~/.local/share/sounds"), "sounds"))
			self.copy_files["install_sounds"] = self.install_sounds
			self.progress_label_sections.append("Sounds")
		if self.install_fonts:
			Path(os.path.expanduser("~/.fonts")).mkdir(parents=True, exist_ok=True)
			self.copy_files.update(self.get_files(running_folder+"/Fonts/", os.path.expanduser("~/.fonts"), "Fonts"))
			self.copy_files["install_fonts"] = self.install_fonts
			self.progress_label_sections.append("Fonts")
		if self.thunar:
			self.copy_files["thunar"] = self.thunar
			self.progress_label_sections.append("Thunar Spinner")
		if self.terminal_colors:
			Path(os.path.expanduser("~/.local/share/xfce4/terminal/colorschemes")).mkdir(parents=True, exist_ok=True)
			Path(os.path.expanduser("~/.config/xfce4/terminal/")).mkdir(parents=True, exist_ok=True)
			self.copy_files[running_folder+"/Extras/Chicago95.theme"] = os.path.expanduser("~/.local/share/xfce4/terminal/colorschemes")
			self.copy_files[running_folder+"/Extras/terminalrc"] = os.path.expanduser("~/.config/xfce4/terminal/")
			if os.path.exists(os.path.expanduser("~/.config/xfce4/terminal/terminalrc")):
				shutil.copyfile(os.path.expanduser("~/.config/xfce4/terminal/terminalrc"),os.path.expanduser("~/.config/xfce4/terminal/backup.terminalrc.chicago95"))
			self.copy_files["terminal_colors"] = self.terminal_colors
			self.progress_label_sections.append("Terminal Colors")
		if self.bash:
			self.copy_files["bash"] = self.bash
			self.progress_label_sections.append("Bash Prompt")
		if self.zsh:
			self.copy_files["zsh"] = self.zsh
			self.progress_label_sections.append("Zsh Prompt")
		if self.panel:
			self.copy_files["panel"] = self.panel
			self.progress_label_sections.append("Panel")

		self.progres_label_names = iter(self.progress_label_sections)
		self.window_installer.hide()
		self.progress_bar = self.builder.get_object('progress bar')
		self.progress_label = self.builder.get_object('progress file')
		self.progress_label_component = self.builder.get_object('progress label')
		self.progress_label_component.set_label("Installing component: {}".format(next(self.progres_label_names)))
		first_file_name = list(self.copy_files.keys())[0].split("/")[-1]
		self.progress_label.set_label(first_file_name)
		self.progress_bar.set_fraction(0.0)
		frac = 1.0 / len(self.copy_files)
		self.progress_window.show_all()
		self.task = self.install()
		self.id = GLib.idle_add(self.task.__next__)

		
	def install(self):
		i = 0.0
		print("Installing Chicago 95")

		for from_file in self.copy_files:
			self.progress_label.set_label(from_file.split("/")[-1])
			i += 1.0
			self.progress_bar.set_fraction(i / len(self.copy_files))
			# copy action here
			if isinstance(self.copy_files[from_file], str):
				if not os.path.isdir(os.path.dirname(self.copy_files[from_file])):
					Path(os.path.dirname(self.copy_files[from_file])).mkdir(parents=True, exist_ok=True)
				try:
					shutil.copy(from_file, self.copy_files[from_file], follow_symlinks=False)
				except FileExistsError:
					pass # We need to do this if we're overwritting the theme cause of symlinks
			else:
				if from_file == "install_theme" and self.copy_files["install_theme"]:
					print("Enabling Theme in XFCE4")
					self.xfconf_query('xsettings', '/Net/ThemeName', "Chicago95")
					self.xfconf_query('xfce4-notifyd', '/theme', "Chicago95")
					self.xfconf_query('xfce4-notifyd', '/initial-opacity', "1.000000")
					self.xfconf_query('xfwm4', '/general/theme', "Chicago95")
					self.xfconf_query('xfwm4', '/general/title_font', "Sans Bold 8")
					self.xfconf_query("xfwm4","/general/shadow_delta_height","0")
					self.xfconf_query("xfwm4","/general/shadow_delta_width","0")
					self.xfconf_query("xfwm4","/general/shadow_delta_x","0")
					self.xfconf_query("xfwm4","/general/shadow_delta_y","-3")
					self.xfconf_query("xfwm4","/general/shadow_opacity","50")
					self.xfconf_query("xfwm4","/general/show_dock_shadow","false")
					self.xfconf_query("xfwm4","/general/show_frame_shadow","false")
					self.xfconf_query("xfwm4","/general/show_popup_shadow","false")
					self.xfconf_query("xfwm4","/general/title_shadow_active","false")
					self.xfconf_query("xfwm4","/general/title_shadow_inactive","false")
					self.change_component_label()

				elif from_file == "install_icons" and self.copy_files["install_icons"]:
					print("Enabling Icons in XFCE4")
					self.xfconf_query('xsettings', '/Net/FallbackIconTheme', 'Adwaita')
					self.xfconf_query('xsettings', '/Net/IconThemeName', "Chicago95")
					self.xfconf_query('xfce4-desktop','/desktop-icons/file-icons/show-filesystem', 'true')
					self.xfconf_query('xfce4-desktop','/desktop-icons/file-icons/show-home', 'true')
					self.xfconf_query('xfce4-desktop','/desktop-icons/file-icons/show-trash','true')
					self.change_component_label()
				elif from_file == "install_background" and self.copy_files["install_background"]:
					print("Changing background")
					r = "{:6f}".format(0/255)
					g = "{:6f}".format(128/255)
					b = "{:6f}".format(128/255)
					a = "1.000000"
					try: 
						self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitorVirtual1/workspace0/image-style', "0")
						args = ['xfconf-query', '-c' ,'xfce4-desktop' ,
							'-p' ,'/backdrop/screen0/monitorVirtual1/workspace0/rgba1' , '--create',
							'-t' ,'double' ,'-s' ,'0.000000' ,'-t' ,'double' ,'-s' ,
							'0.500000' ,'-t' ,'double' ,'-s', '0.500000' ,'-t' ,'double' ,
							'-s' ,'1.000000']
						subprocess.check_call(args, stdout=subprocess.DEVNULL)	
					except subprocess.CalledProcessError:
						try:
							self.xfconf_query('xfce4-desktop', '/backdrop/screen0/monitor0/workspace0/image-style', "0")
							args = ['xfconf-query', '-c' ,'xfce4-desktop' ,
								'-p' ,'/backdrop/screen0/monitor0/workspace0/rgba1' ,
								'-t' ,'double' ,'-s' ,'0.000000' ,'-t' ,'double' ,'-s' ,
								'0.500000' ,'-t' ,'double' ,'-s', '0.500000' ,'-t' ,'double' ,
								'-s' ,'1.000000']
							subprocess.check_call(args, stdout=subprocess.DEVNULL)	
						except:
							print("Could not update background. Set your background manually to #008080")
					except:
						print("Could not update background. Set your background manually to #008080")
					self.change_component_label()

				elif from_file == "install_cursors" and self.copy_files["install_cursors"]:
					print("Enabling Cursors in XFCE4")
					self.xfconf_query('xsettings', '/Gtk/CursorThemeName', "Chicago95 Standard Cursors")
					self.change_component_label()
				elif from_file == "install_sounds" and self.copy_files["install_sounds"]:
					print("Enabling Sounds in XFCE4")
					self.xfconf_query('xsettings', '/Net/EnableEventSounds', "true")
					self.xfconf_query('xsettings', '/Net/EnableInputFeedbackSounds', "true")
					self.xfconf_query('xsettings', '/Net/SoundThemeName', "Chicago95")
					self.change_component_label()
				elif from_file == "install_fonts" and self.copy_files["install_fonts"]:
					print("Enabling Fonts in XFCE4")
					self.change_component_label()
          # LOL this is a lie we don't have to do anything
				elif from_file == "thunar" and self.copy_files["thunar"]:
					if os.path.exists(os.path.expanduser("~/.themes/Chicago95/gtk-3.24/apps/thunar.css")):
						print("Enabling authenticity in Thunar")
						shutil.move( os.path.expanduser("~/.themes/Chicago95/gtk-3.24/apps/thunar.css"),os.path.expanduser("~/.themes/Chicago95/gtk-3.24/apps/thunar.css.bak") )
						fileh = open(os.path.expanduser("~/.themes/Chicago95/gtk-3.24/apps/thunar.css.bak"),"r")
						nfileh = open(os.path.expanduser("~/.themes/Chicago95/gtk-3.24/apps/thunar.css"),"w")
						next_line = False
						for line in fileh:
							if next_line:
								if "/*" in line:
									line = line.replace("/*","")
								if "c95" in line:
									line = line.replace("c95", "msw")
								if "*/" in line:
									line = line.replace("*/","")
									next_line = False

							if "You can enable the spin button theme by uncommenting the following!" in line:
								next_line = True
							nfileh.write(line)
						fileh.close()
						nfileh.close()
					else:
						print("Chicago95 theme not installed, cannot modify thunar")
					self.change_component_label()
				elif from_file == "terminal_colors" and self.copy_files["terminal_colors"]:
					print("Enabling Terminal color theme")
					self.change_component_label()
					# This is done through the copy/paste of terminalrc
				elif from_file == "bash" and self.copy_files["bash"]:
					print("Enabling bash prompt")
					prompts_file = open(running_folder+"/Extras/DOSrc", "r")
					prompts = prompts_file.read()
					prompts_file.close()
					if os.path.exists(os.path.expanduser("~/.bashrc")):
						shutil.copyfile(os.path.expanduser("~/.bashrc"),os.path.expanduser("~/.config/xfce4/terminal/backup.bashrc.chicago95"))
						bashrc_out = open(os.path.expanduser("~/.bashrc"), "a")
						bashrc_out.write(prompts)
						bashrc_out.close()
					else:
						bashrc_out = open(os.path.expanduser("~/.bashrc"), "w")
						bashrc_out.write(prompts)
						bashrc_out.close()
					self.change_component_label()
		
				elif from_file == "zsh" and self.copy_files["zsh"]:
					if os.path.exists(os.path.expanduser("~/.oh-my-zsh")):
						print("Enabling zsh theme/prompt")

						prompts_file = open(running_folder+"/Extras/ZSHDOSrc", "r")
						prompts = prompts_file.read()
						prompts_file.close()

						shutil.copyfile(running_folder+"/Extras/Chicago95.zsh-theme", os.path.expanduser("~/.oh-my-zsh/themes/Chicago95.zsh-theme"))
						shutil.move( os.path.expanduser("~/.zshrc"),os.path.expanduser("~/.backup.zshrc.chicago95") )
						fileh = open(os.path.expanduser("~/.backup.zshrc.chicago95"),"r")
						nfileh = open(os.path.expanduser("~/.zshrc"),"w")
						for line in fileh:
							if "ZSH_THEME" in line:
								line = "ZSH_THEME=Chicago95"
							nfileh.write(line)
						fileh.close()
						nfileh.close()
					else:
						print("Oh my zsh not installed, cannot install theme")
					self.change_component_label()
				elif from_file == "panel" and self.copy_files["panel"]:
					print("Generating XFCE panel")
					print("Installing Panel config from: "+ running_folder +"/Extras/Chicago95_Panel_Preferences.tar.bz2")
					#xfce4-panel-profiles load Extras/Chicago95_Panel_Preferences.tar.bz2
					subprocess.check_call(["xfce4-panel-profiles", "load", running_folder+"/Extras/Chicago95_Panel_Preferences.tar.bz2"], stdout=subprocess.DEVNULL)
					self.change_component_label()
					
			gc.collect()
			yield True

		stack = self.builder.get_object('stack')
		stack.set_visible_child(stack.get_child_by_name('page_completed'))
		self.progress_window.hide()
		next_button = self.builder.get_object('next')
		back_button = self.builder.get_object('back')
		back_button.set_sensitive(False)
		next_button.set_label("Finish")
		self.window_installer.show_all()
		GLib.source_remove(self.id)
		subprocess.Popen(["mousepad", running_folder+"/Extras/post_install.txt"])
		yield False


	def change_component_label(self):
		try:
			self.progress_label_component.set_label("Installing component: {}".format(next(self.progres_label_names)))
		except:
			pass


	def xfconf_query(self, channel, prop, new_value):
		
		try:
			xfconf_query_path = subprocess.check_output(["which", "xfconf-query"]).strip()
		except:
			print("Warning: xfconf-query not installed, cannot auto-enable theme. Use your distros theme management to install Chicago95")
			return

		try:

			print("Changing xfconf setting {}/{} to {}".format(channel, prop, new_value))
			args = [
				xfconf_query_path,
				"--channel", channel,
				"--property", prop,
				"--set", new_value
				]
			subprocess.check_call(args, stdout=subprocess.DEVNULL)

		except subprocess.CalledProcessError:

			print("Changing xfconf setting {}/{} to {}".format(channel, prop, new_value))
			args = [
				xfconf_query_path,
				"--channel", channel,
				"--property", prop,
				"--create", "--type", "string",
				"--set", new_value
				]
			subprocess.check_call(args, stdout=subprocess.DEVNULL)	

	def check_xfce_panel(self):	

		try:
			xfce_panel = subprocess.check_output(["which", "xfce4-panel-profiles"]).strip()
		except subprocess.CalledProcessError:
			return False
		return True



	def cancel_install(self, button):
		print("Cancelling Install")
		Gtk.main_quit()
		return False

	def get_files(self, from_folder, target_folder, target):		
		theme_files = {}
		for root, dirs, files in os.walk(from_folder):

			if root[-1] != "/":
				root = root + "/"

			loc = root.find(target)
			to_dir = root[loc+len(target):]

			for folder in dirs:
				if os.path.islink(os.path.join(root,folder)):
					from_file = "{}{}".format(root, folder)
					to_file = "{}{}{}".format(target_folder,to_dir, folder)
					theme_files[from_file] = to_file

			for name in files:
				from_file = "{}{}".format(root, name)
				to_file = "{}{}{}".format(target_folder,to_dir, name)
				theme_files[from_file] = to_file

		return theme_files	

	# Set toggle handling

	def set_install_theme(self, toggle):
		if self.install_theme:
			self.install_theme = False
			self.total_size_kb = self.total_size_kb - self.theme_size_kb
			self.theme_size.set_label("{} k".format(0))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb - self.theme_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		else:
			self.install_theme = True
			self.total_size_kb = self.total_size_kb + self.theme_size_kb
			self.theme_size.set_label("{} k".format(self.theme_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb + self.theme_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		

	def set_install_icons(self, toggle):
		if self.install_icons:
			self.install_icons = False
			self.total_size_kb = self.total_size_kb - self.icons_size_kb
			self.icons_size.set_label("{} k".format(0))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb - self.icons_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		else:
			self.install_icons = True
			self.total_size_kb = self.total_size_kb + self.icons_size_kb
			self.icons_size.set_label("{} k".format(self.icons_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb + self.icons_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))

	def set_install_cursors(self, toggle):
		if self.install_cursors:
			self.install_cursors = False
			self.total_size_kb = self.total_size_kb - self.cursors_size_kb
			self.cursors_size.set_label("{} k".format(0))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb - self.cursors_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		else:
			self.install_cursors = True
			self.total_size_kb = self.total_size_kb + self.cursors_size_kb
			self.cursors_size.set_label("{} k".format(self.cursors_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb + self.cursors_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))

	def set_install_background(self, toggle):
		if self.install_background:
			self.install_background = False
		else:
			self.install_background = True

	def set_install_sounds(self, toggle):
		if self.install_sounds:
			self.install_sounds = False
			self.total_size_kb = self.total_size_kb - self.sounds_size_kb
			self.sounds_size.set_label("{} k".format(0))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb - self.sounds_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		else:
			self.install_sounds = True
			self.total_size_kb = self.total_size_kb + self.sounds_size_kb
			self.sounds_size.set_label("{} k".format(self.sounds_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb + self.sounds_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))

	def set_install_fonts(self, toggle):
		if self.install_fonts:
			self.install_fonts = False
			self.total_size_kb = self.total_size_kb - self.fonts_size_kb
			self.fonts_size.set_label("{} k".format(0))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb - self.fonts_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))
		else:
			self.install_fonts = True
			self.total_size_kb = self.total_size_kb + self.fonts_size_kb
			self.fonts_size.set_label("{} k".format(self.fonts_size_kb))
			self.remaining_size.set_label("{:.0f} k".format(int(self.available_kb - self.total_size_kb + self.fonts_size_kb)))
			self.total_size.set_label("{} k".format(self.total_size_kb))

	def set_change_thunar(self, toggle):
		if self.thunar:
			self.thunar = False
		else:
			self.thunar = True

	def set_change_terminal(self, toggle):
		if self.terminal_colors:
			self.terminal_colors = False
		else:
			self.terminal_colors = True

	def set_change_bash(self, toggle):
		if self.bash:
			self.bash = False
		else:
			self.bash = True

	def set_change_zsh(self, toggle):
		if self.zsh:
			self.zsh = False
		else:
			self.zsh = True

	def set_change_panel(self, toggle):
		if self.panel:
			self.panel = False
		else:
			self.panel = True


app = InstallGUI()
Gtk.main()
