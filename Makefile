# File: Makefile for Chicago95
# Location: Chicago95 source package
# License: CC-BY-SA 4.0
# Author: bgstack15
# Title: Makefile for Chicago95 source package
# Purpose: Group theme files for easy installation and uninstallation
# History:
# Usage:
# Reference:
#    spaces and underscores https://ftp.gnu.org/old-gnu/Manuals/make-3.79.1/html_chapter/make_6.html
# Improve:
# Dependencies:
#    build-dpkg: txt2man

APPNAME    = chicago95
APPVERSION = 2.0.1
SRCDIR     = $(CURDIR)
BUILDDIR   = $(CURDIR)
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
MIMEDIR    = $(SHAREDIR)/mime/packages
MANDIR     = $(SHAREDIR)/man
XDGAUTODIR = $(SYSCONFDIR)/xdg/autostart
FONTDIR    = $(SHAREDIR)/fonts
THEMESDIR  = $(SHAREDIR)/themes
SOUNDSDIR  = $(SHAREDIR)/sounds
BKGDSDIR   = $(SHAREDIR)/backgrounds/Chicago95

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
txt2manbin :=$(shell which txt2man)

use_underscores ?= NO

.PHONY: clean install install_files build_man uninstall list deplist deplist_opts build_man

nullstring :=
space :=\ $(nullstring)# end of the line
ifeq ($(use_underscores),YES)
space = _
endif

all: build_man

list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | ${awkbin} -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | ${sortbin} | ${grepbin} -E -v -e '^[^[:alnum:]]' -e '^$@$$'

build_man:
	@# these man pages are installed with install_plus
	@test -d ${BUILDDIR} || mkdir -p ${BUILDDIR}
	${txt2manbin} -P chicago95-theme-plus -r chicago95-theme-plus -d "June 2020" -t "PlusGUI" -s 1 -v "General Commands Manual" < ${SRCDIR}/Plus/PlusGUI.1.txt | ${gzipbin} > ${BUILDDIR}/PlusGUI.1.gz
	${txt2manbin} -P chicago95-theme-plus -r chicago95-theme-plus -d "June 2020" -t "Chicago95" -s 1 -v "General Commands Manual" < ${SRCDIR}/Plus/ChicagoPlus.1.txt | ${gzipbin} > ${BUILDDIR}/ChicagoPlus.1.gz

install: install_all

.PHONY: install_cursors install_doc install_fonts install_gtk_theme install_icons install_sounds install_login_sound install_boot_screen install_plus install_backgrounds
install_all: install_cursors install_doc install_fonts install_gtk_theme install_icons install_sounds install_login_sound install_boot_screen install_plus install_backgrounds

install_cursors:
	${installbin} -dm0755 \
		${ICONSDIR}/Chicago95$(space)Animated$(space)Hourglass$(space)Cursors \
		${ICONSDIR}/Chicago95_Cursor_Black \
		${ICONSDIR}/Chicago95_Cursor_White \
		${ICONSDIR}/Chicago95_Emerald \
		${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors$(space)Black \
		${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors \

	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95\ Animated\ Hourglass\ Cursors/* ${ICONSDIR}/Chicago95$(space)Animated$(space)Hourglass$(space)Cursors
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Cursor_Black/* ${ICONSDIR}/Chicago95_Cursor_Black
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Cursor_White/* ${ICONSDIR}/Chicago95_Cursor_White
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95_Emerald/* ${ICONSDIR}/Chicago95_Emerald
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95\ Standard\ Cursors/* ${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors
	${cpbin} -pr ${SRCDIR}/Cursors/Chicago95\ Standard\ Cursors\ Black/* ${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors$(space)Black
	${findbin} ${ICONSDIR}/Chicago95* ! -type d -exec ${chmodbin} 0644 {} +

install_doc:
	${installbin} -dm0755 ${DOCDIR}
	${installbin} -m0644 -t ${DOCDIR} ${SRCDIR}/*md Screenshots/SCREENSHOTS.md
	@# rename a few files
	${installbin} -m0644 ${SRCDIR}/Plymouth/README.md ${DOCDIR}/Plymouth-readme.md
	${installbin} -m0644 ${SRCDIR}/Lightdm/Chicago95/README.md ${DOCDIR}/Lightdm-readme.md
	${installbin} -m0644 -t ${DOCDIR} ${SRCDIR}/Extras/post_install.txt

install_fonts:
	${installbin} -dm0755 ${FONTDIR}/truetype
	${installbin} -m0644 -t ${FONTDIR}/truetype ${SRCDIR}/Fonts/vga_font/*ttf

install_gtk_theme:
	${installbin} -dm0755 ${THEMESDIR}
	${cpbin} -pr ${SRCDIR}/Theme/Chicago95 ${THEMESDIR}
	${rmbin} -r ${THEMESDIR}/Chicago95/misc
	${findbin} ${THEMESDIR}/Chicago95 ! -type d -exec ${chmodbin} 0644 {} + || :
	${findbin} ${THEMESDIR}/Chicago95 -type d -exec ${chmodbin} 0755 {} + || :
	@# xfce4-terminal theme
	${installbin} -dm0755 ${SHAREDIR}/xfce4/terminal/colorschemes
	${installbin} -m0644 -t ${SHAREDIR}/xfce4/terminal/colorschemes ${SRCDIR}/Extras/Chicago95.theme
	@# panel profile
	${installbin} -dm0755 ${SHAREDIR}/xfce4-panel-profiles/layouts
	${installbin} -m0644 -t ${SHAREDIR}/xfce4-panel-profiles/layouts ${SRCDIR}/Extras/Chicago95_Panel_Preferences.tar.bz2

install_icons:
	${installbin} -dm0755 ${ICONSDIR}
	${cpbin} -pr ${SRCDIR}/Icons/* ${ICONSDIR}/
	${findbin} ${ICONSDIR}/Chicago95* ! -type d ! -type l -exec ${chmodbin} 0644 {} +

install_sounds:
	${installbin} -dm0755 ${SOUNDSDIR}/Chicago95/stereo
	${installbin} -m0644 -t ${SOUNDSDIR}/Chicago95/stereo ${SRCDIR}/sounds/Chicago95/stereo/*
	${installbin} -m0644 -t ${SOUNDSDIR}/Chicago95 ${SRCDIR}/sounds/Chicago95/index.theme

install_login_sound:
	${installbin} -dm0755 ${SOUNDSDIR}/Chicago95 ${XDGAUTODIR}
	${installbin} -m0644 ${SRCDIR}/Extras/Microsoft\ Windows\ 95\ Startup\ Sound.ogg ${SOUNDSDIR}/Chicago95/startup.ogg
	${installbin} -m0644 -t ${XDGAUTODIR} ${SRCDIR}/sounds/chicago95-startup.desktop

install_boot_screen:
	${installbin} -dm0755 ${SHAREDIR}/plymouth/themes/Chicago95 ${SHAREDIR}/plymouth/themes/RetroTux
	${installbin} -m0644 -t ${SHAREDIR}/plymouth/themes/Chicago95 ${SRCDIR}/Plymouth/Chicago95/*
	${installbin} -m0644 -t ${SHAREDIR}/plymouth/themes/RetroTux ${SRCDIR}/Plymouth/RetroTux/*

install_plus:
	${installbin} -dm0755 ${SHAREDIR}/chicago95-theme-plus/assets ${BINDIR} ${LIBEXECDIR}/chicago95-theme-plus ${DOCDIR}/demo ${APPSDIR} ${MIMEDIR} ${MANDIR}/man1
	${installbin} -m0644 -t ${SHAREDIR}/chicago95-theme-plus/assets ${SRCDIR}/Plus/assets/*
	${installbin} -m0755 ${SRCDIR}/Plus/ChicagoPlus.py ${BINDIR}/ChicagoPlus
	${installbin} -m0755 ${SRCDIR}/Plus/PlusGUI.py ${BINDIR}/PlusGUI
	${installbin} -m0644 -t ${LIBEXECDIR}/chicago95-theme-plus ${SRCDIR}/Plus/pluslib.py ${SRCDIR}/Plus/plus.glade
	${installbin} -m0644 ${SRCDIR}/Plus/README.MD ${DOCDIR}/Plus-README.MD
	${installbin} -m0644 -t ${DOCDIR} ${SRCDIR}/Plus/*.png
	${installbin} -m0644 -t ${DOCDIR}/demo ${SRCDIR}/Plus/demo/*
	${installbin} -m0644 -t ${APPSDIR} ${SRCDIR}/Plus/*.desktop
	${installbin} -m0644 -t ${MIMEDIR} ${SRCDIR}/Plus/chicago95-plus-theme.xml
	${installbin} -m0644 -t ${MANDIR}/man1 ${BUILDDIR}/*.1.gz

install_backgrounds:
	${installbin} -dm0755 ${BKGDSDIR}/patterns ${BKGDSDIR}/wallpapers
	${installbin} -m0644 -t ${BKGDSDIR}/patterns ${SRCDIR}/Extras/Backgrounds/Patterns/*
	${installbin} -m0644 -t ${BKGDSDIR}/wallpapers ${SRCDIR}/Extras/Backgrounds/Wallpaper/*

uninstall:
	${rmbin} -rf \
		${ICONSDIR}/Chicago95$(space)Animated$(space)Hourglass$(space)Cursors \
		${ICONSDIR}/Chicago95_Cursor_Black \
		${ICONSDIR}/Chicago95_Cursor_White \
		${ICONSDIR}/Chicago95_Emerald \
		${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors$(space)Black \
		${ICONSDIR}/Chicago95$(space)Standard$(space)Cursors \
		${DOCDIR} \
		${FONTDIR}/truetype/LessPerfectDOSVGA.ttf \
		${FONTDIR}/truetype/MorePerfectDOSVGA.ttf \
		${SHAREDIR}/lightdm-webkit/themes/Chicago95 \
		${THEMESDIR}/Chicago95 ${SHAREDIR}/xfce4/terminal/colorschemes/Chicago95.theme \
		${SHAREDIR}/xfce4-panel-profiles/layouts/Chicago95_Panel_Preferences.tar.bz2 \
		${ICONSDIR}/Chicago95 ${ICONSDIR}/Chicago95-tux \
		${SOUNDSDIR}/Chicago95 \
		${LIBEXECDIR}/chicago95-theme-plus ${BINDIR}/ChicagoPlus ${BINDIR}/PlusGUI \
		${SHAREDIR}/chicago95-theme-plus \
		${APPSDIR}/PlusGUI.desktop ${MIMEDIR}/chicago95-plus-theme.xml \
		${MANDIR}/man1/ChicagoPlus.1.gz ${MANDIR}/man1/PlusGUI.1.gz \
		${SHAREDIR}/plymouth/themes/Chicago95 ${SHAREDIR}/plymouth/themes/RetroTux \
		${BKGDSDIR} \
		${XDGAUTODIR}/chicago95-startup.desktop

clean:
	-${rmbin} ${BUILDDIR}/*.1.gz
