# File: Makefile for Chicago95
# Location: Chicago95 source package
# License: CC-BY-SA 4.0
# Author: bgstack15
# Title: Makefile for Chicago95 source package
# Purpose: Group theme files for easy installation and uninstallation
# History:
# Usage:
# Reference:
# Improve:
# Dependencies:

APPNAME    = chicago95
APPVERSION = 0.0.2beta
SRCDIR     = $(CURDIR)
prefix     = /usr
SYSCONFDIR = $(DESTDIR)/etc
DEFAULTDIR = $(DESTDIR)/etc/sysconfig # for debian use '$(DESTDIR)/etc/default'
BINDIR     = $(DESTDIR)$(prefix)/bin
LIBEXECDIR = $(DESTDIR)$(prefix)/libexec
SBINDIR    = $(DESTDIR)$(prefix)/sbin
SHAREDIR   = $(DESTDIR)$(prefix)/share
DOCDIR     = $(SHAREDIR)/doc/$(APPNAME)
APPDIR     = $(SHAREDIR)/$(APPNAME)
APPSDIR    = $(SHAREDIR)/applications
ICONSDIR   = $(SHAREDIR)/icons
MIMEDIR    = $(SHAREDIR)/mime
MANDIR     = $(SHAREDIR)/man
XDGAUTODIR = $(SYSCONFDIR)/xdg/autostart
FONTDIR    = $(SHAREDIR)/fonts
THEMESDIR  = $(SHAREDIR)/themes
SOUNDSDIR  = $(SHAREDIR)/sounds

awkbin     :=$(shell which awk)
chmodbin   :=$(shell which chmod)
cpbin      :=$(shell which cp)
echobin    :=$(shell which echo)
falsebin   :=$(shell which false)
findbin    :=$(shell which find)
grepbin    :=$(shell which grep)
gzipbin    :=$(shell which gzip)
installbin :=$(shell which install)
rmbin      :=$(shell which rm)
rmdirbin   :=$(shell which rmdir)
sedbin     :=$(shell which sed)
sortbin    :=$(shell which sort)
truebin    :=$(shell which true)
uniqbin    :=$(shell which uniq)
xargsbin   :=$(shell which xargs)

.PHONY: clean install install_files build_man uninstall list deplist deplist_opts

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | ${awkbin} -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | ${sortbin} | ${grepbin} -E -v -e '^[^[:alnum:]]' -e '^$@$$'

install: install_all

install_all: install_cursors install_doc install_fonts install_greeter install_gtk_theme install_icons install_login_sound install_boot_screen

install_cursors:
	${installbin} -dm0755 ${ICONSDIR}/Chicago95_Cursor_Black \
		${ICONSDIR}/Chicago95_Cursor_White \
		${ICONSDIR}/Chicago95_Emerald
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Cursor_Black/* ${ICONSDIR}/Chicago95_Cursor_Black
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Cursor_White/* ${ICONSDIR}/Chicago95_Cursor_White
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Emerald/* ${ICONSDIR}/Chicago95_Emerald
	${findbin} ${ICONSDIR}/Chicago95* ! -type d -exec ${chmodbin} 0644 {} +

install_doc:
	${installbin} -dm0755 ${DOCDIR}
	${installbin} -m0644 -t ${DOCDIR} ${SRCDIR}/*md Screenshots/SCREENSHOTS.md
	@# rename a few files
	${installbin} -m0644 ${SRCDIR}/Plymouth/Readme.md ${DOCDIR}/Plymouth-readme.md
	${installbin} -m0644 ${SRCDIR}/Lightdm/Chicago95/README.md ${DOCDIR}/Lightdm-readme.md

install_fonts:
	${installbin} -dm0755 ${FONTDIR}/truetype
	${installbin} -m0644 -t ${FONTDIR}/truetype ${SRCDIR}/Fonts/vga_font/*ttf

install_greeter:
	${installbin} -dm0755 ${SHAREDIR}/lightdm-webkit/themes
	${cpbin} -pr ${SRCDIR}/Lightdm/Chicago95 ${SHAREDIR}/lightdm-webkit/themes/
	${findbin} ${SHAREDIR}/lightdm-webkit/themes/Chicago95 ! -type d -exec ${chmodbin} 0644 {} +

install_gtk_theme:
	${installbin} -dm0755 ${THEMESDIR}
	${cpbin} -pr ${SRCDIR}/Theme/Chicago95 ${THEMESDIR}
	${rmbin} -r ${THEMESDIR}/Chicago95/misc
	${findbin} ${THEMESDIR}/Chicago95 ! -type d -exec ${chmodbin} 0644 {} +
	@# xfce4-terminal theme
	${installbin} -dm0755 ${SHAREDIR}/xfce4/terminal/colorschemes
	${installbin} -m0644 -t ${SHAREDIR}/xfce4/terminal/colorschemes ${SRCDIR}/Extras/Chicago95.theme

install_icons:
	${installbin} -dm0755 ${ICONSDIR}
	${cpbin} -pr ${SRCDIR}/Icons/* ${ICONSDIR}/
	${findbin} ${ICONSDIR}/Chicago95* ! -type d ! -type l -exec ${chmodbin} 0644 {} +

install_login_sound:
	${installbin} -dm0755 ${SOUNDSDIR}/Chicago95
	# pending addition of debian/chicago95-startup.desktop to source ${XDGAUTODIR}
	${installbin} -m0644 ${SRCDIR}/Extras/Microsoft\ Windows\ 95\ Startup\ Sound.ogg ${SOUNDSDIR}/Chicago95/startup.ogg
	# pending addition of debian/chicago95-startup.desktop to source ${XDGAUTODIR}
	#${installbin} -m0644 -t ${XDGAUTODIR} ${SRCDIR}/Extras/chicago95-startup.desktop

install_boot_screen:
	${installbin} -dm0755 ${SHAREDIR}/plymouth/themes/Chicago95 ${SHAREDIR}/plymouth/themes/RetroTux
	${installbin} -m0644 -t ${SHAREDIR}/plymouth/themes/Chicago95 ${SRCDIR}/Plymouth/Chicago95/*
	${installbin} -m0644 -t ${SHAREDIR}/plymouth/themes/RetroTux ${SRCDIR}/Plymouth/RetroTux/*

uninstall:
	${rmbin} -r ${ICONSDIR}/Chicago95_Cursor_Black \
		${ICONSDIR}/Chicago95_Cursor_White \
		${ICONSDIR}/Chicago95_Emerald \
		${DOCDIR} \
		${FONTDIR}/truetype/LessPerfectDOSVGA.ttf \
		${FONTDIR}/truetype/MorePerfectDOSVGA.ttf \
		${SHAREDIR}/lightdm-webkit/themes/Chicago95 \
		${THEMESDIR}/Chicago95 ${SHAREDIR}/xfce4/terminal/colorschemes/Chicago95.theme \
		${ICONSDIR}/Chicago95 ${ICONSDIR}/Chicago95-tux \
		${SOUNDSDIR}/Chicago95 \
		${SHAREDIR}/plymouth/themes/Chicago95 ${SHAREDIR}/plymouth/themes/RetroTux 2>/dev/null || :

clean:
	-@${echobin} "target $@ not implemented yet! Gotta say unh." && ${falsebin}
