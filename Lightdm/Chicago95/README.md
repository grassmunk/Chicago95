Chicago95 Greeter
===================

Chicago95 is a greeter (a login screen) for use with lightdm and lightdm-webkit-greeter.

It has very limited functionality, but reminds you of that 90s aesthetic.

Documentation
-------------

You'll need to have lightdm and lightdm-webkit for this to work. On Xubuntu, you'd do something like:

    sudo apt-get install lightdm lightdm-webkit-greeter

First, configure lightdm to use lightdm-webkit-greeter if you haven't already. To do so, open up `/etc/lightdm/lightdm.conf` with a text editor and change it to something like this:

```
[SeatDefaults]
greeter-session=lightdm-webkit-greeter
user-session=xfce
```

Secondly, you need to copy the `LessPerfect DOS VGA` font from the `Fonts/vga_font` directory of this repository to somewhere in `/usr/share/fonts`.

Follow these steps:
```
sudo cp -v Chicago95-master/Fonts/vga_font/LessPerfectDOSVGA.ttf /usr/share/fonts
```

Then, refresh the font cache with:
```
sudo fc-cache -fv
```

Next, configure lightdm-webkit-greeter to use *Chicago95*. You can do so by editing `/etc/lightdm/lightdm-webkit-greeter.conf` and setting `theme-name`to `Chicago95`:

```
# background = Background file to use, either an image path or a color (e.g. #772953)
# theme-name = GTK+ theme to use
# font-name = Font to use
# xft-antialias = Whether to antialias Xft fonts (true or false)
# xft-dpi = Resolution for Xft in dots per inch (e.g. 96)
# xft-hintstyle = What degree of hinting to use (hintnone, hintslight, hintmedium, or hintfull)
# xft-rgba = Type of subpixel antialiasing (none, rgb, bgr, vrgb or vbgr)
#
[greeter]
webkit-theme=Chicago95
```


Finally, copy the Chicago95 folder to the lightdm webkit themes folder: `/usr/share/lightdm-webkit/themes/`.

Dependencies
------------

lightdm, lightdm-webkit-greeter and those nostalgic feels

License
-------

This greeter is MIT-licensed, but few people care. Check out the LICENSE file if you think you've got what it takes.

Credits
-------

This theme was based on paddy-greeter which you can find here: 

*   [Paddy-Greeter](https://github.com/kalmanolah/paddy-greeter/) by [Kalman Olah](https://github.com/kalmanolah/)

Button theming was copied from win95.css:
*   [Win95.CSS](https://github.com/AlexBSoft/win95.css) by [Aleksander Bakukhin](https://github.com/AlexBSoft)

The key icon was found here:
*   [Windows95 All Icons](https://archive.org/details/windows-95-all-icons) by [Vovan29](https://archive.org/search?query=creator%3A%22Vovan29%22)
