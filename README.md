# Chicago95

## XFCE / Xubuntu Windows 95 Total Conversion

I was unhappy with the various XFCE/GTK2/GTK3 Windows 95 based themes and decided to make one that was more consistent accross the board for theming.

Included in this theme:

- New icons to complete the icon theme started with Classic95
- Edited Redmond XFWM theme to more accurately reflect Windows 95
- Edited Xfce-Redmond by dbbolton to be more accurate and include XFCE panels
- Created GTK-3.0 theme from scratch (based on Win 10 and Mate themes)
- Plymouth theme created from scratch
- An MS-DOS inspired theme for oh-my-zsh

## Screenshots
![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/plymouth.gif "Plymouth")

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/lightdm.png "LightDM")

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/Screenshot.png "Big Screenshot")

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/gtk2.png "GTK2")

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/widget-factory-gtk3-chicago95.png "GTK3")

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/nautilus-grk3-chicago95.png "GTK3")


I decided that the pop-overs were almost exactly as annoying/ugly as Clippy was in MS Office 97 so the buttons/coloring are matched to look exactly like that.

![alt text](https://raw.githubusercontent.com/AdrianoML/Chicago95/master/Screenshots/DOS.png "Terminal")

There is also an oh-my-zsh terminal theme.

![alt text](https://raw.githubusercontent.com/Geweldig/Chicago95/master/Screenshots/oh-my-zshDOS.png "oh-my-zsh terminal")

## Installation

### Themes
For system wide install, copy the folder `Theme/Chicago95` to the themes directory i.e. `/usr/share/themes/` or `~/.themes`.

In XFCE select Settings -> Appearance. Click on 'Style' and select `Chicago95`.

For window borders select Settings -> Window Manager. Under 'Style' select `Chicago 95`.

Background: Just set to whatever you like, for a more authentic look try setting Style to none and color to `#008080`.

###  Icons
To install the icons copy the folder `Icons/Chicago95` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Appearance. Click on 'Icons' and select `Chicago95`.

For icons with tux check the Extras section below.

### Cursors
To install the cursors copy the folders in `Cursors` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Mouse and Touchpad. Click on 'Icons' and select `Chicago95`.

### Fonts
Copy the folder `Fonts/vga_font` to `~/.fonts/truetype/` if the `.fonts/truetype` folder doesn't exist just create it before you copy the files. 

Update your font cache: sudo fc-cache -f -v

In xfce-term selet the font `Less Perfect DOS VGA` or `More Pefect DOS VGA`.

### Terminal
#### Bash
Copy the file `Extras/Chicago95.theme` to `~/.local/share/xfce4/terminal/colorschemes` (create the colorschemes folder if it doesn't exist: `mkdir .local/share/xfce4/terminal`).
Under preferences in xfce-term select 'Colors.' Under `Presets` you should see `Chicago 95`.

To get the MS-DOS `C:\>` prompt and startup message add the contents of `Extras/DOSrc` to your `.bashrc` file: `cat Extras/DOSrc >> ~/.bashrc`.
To get MS-DOS Prompt title, go to the Preferences prompt and change title to MS-DOS Prompt and select isn't displayed on The Dynamically-Set Title

#### oh-my-zsh
Copy the file `Extras/Chicago95.zsh-theme` to `~/.oh-my-zsh/themes` (if you have changed your `.oh-my-zsh` config location, put the theme in that folder). In your `.zshrc` change your theme to Chicago95.

This will add the MS-DOS prompt. You will get a C prompt by default. If the previous command had an exit code other than 0 you will get an F prompt. If you are in a git repository you will git a G prompt, followed by the branch (in yellow) and the status (clean in green, dirty in red).

To get the startup message, add the contents of `Extras/ZSHDOSrc` to your `.zshrc` file: `cat Extras/ZSHDOSrc >> ~/.zshrc`.

### Plymouth

Recreates the classic Windows 95 boot screen.

To install:

```
sudo cp -r Plymouth/Chicago95 /lib/plymouth/themes/
sudo update-alternatives --install /lib/plymouth/themes/default.plymouth default.plymouth /lib/plymouth/themes/Chicago95/Chicago95.plymouth 100
sudo update-alternatives --config default.plymouth  #here, choose the number of the theme you want to use then hit enter
sudo update-initramfs -u
```

### LightDM:

Attemps to recreate the asthetic of logging on to a computer in the mid 90's.

Install instructions are in the `README.md` in `Lightdm/Chicago95/`.


## Extras

Big thanks to u/EMH_Mark_I at Reddit.com for the most recent changes and these items:

### Fonts
In the xfce appearance window, open the font tab.

* Default Font: Sans 10
* Enable Antialiasing: Yes
* Hinting: Full
* Sub-pixel order: None

Next, open Window Manager.

* Title Font: Sans Bold 8

### Where’s the classic Start Button?

If you want a classic style start button for the Whisker Menu or Application-Menu plugins instead of it defaulting to only an icon without the button borders, there are a few steps required to set this up.

Note: Your panel has to be 32px high if you wish to have the classic style Start button. If it’s any other size, the button won’t look correct. You’re more than welcomed to make your own Start button.
This is a work around because I’ve been unable to find a more sane means of making something that should be so simple to work...

1. Go to the install directory of the theme, i.e.`~/.themes/Chicago95/gtk-2.0/` or `/usr/share/themes/Chicago95/gtk-2.0/.`
2. You will see a file named `panel.rc` and another one named `panel.rc.alt`. Rename `panel.rc` to `panel.rc.bak`. Then rename `panel.rc.alt` to `panel.rc`.
3. Open the properties menu of either Whisker Menu or Application Menu and change the icon. The Start Button is located in the following directory: `~/.themes/Chicago95/gtk-2.0/panel` or `/usr/share/themes/Chicago95/gtk-2.0/panel.` Select the file name `start-button_windows` or `start-button_tux.`
4. The icon will appear crunched. Log out and log back in or run `xfce4-panel -r` to reset the panel interface. The icon should appear a regular size.

### Pulse Audio Icon Fix
Copy the `pulseaudio_fix.css` file from the `Extras\gtk-3.0 Override` directory into `/home/$USER/.config/gtk-3.0/` (This will fix the oversized pulse audio button and battery icon in the panel.)

Next, execute the following command as a regular user to import the pulseaudio fix:

`echo "@import url(\"pulseaudio_fix.css\");" >> /home/$USER/.config/gtk-3.0/gtk.css`

### Setting up the panel

1. Panel 1. Horizontal, 32px high ONLY, and 100% Length. Currently no proper vertical panel support so below or above only. (Make sure you set the background style to "None" so that it inherits the theme style.)
2. Application Menu; 
3. Separator (Handle Style); 
4. Custom Launcher, Custom Launcher, Custom Launcher, etc. (Try using 16px icons for the launchers.)
5. “Show Desktop” plugin; 
6. Separator (Handle Style); 
7. Window Buttons (Sorting Order: Timestamp and Window Grouping is Always. Uncheck “Show Handle” if it’s enabled.); 
8. Separator (Transparent with Expanding); 
9. Separator (Handle Style); 
10. Notification Area (19px max icon size); 
11. PulseAudio Plugin (Uncheck mark "Show Notifications when volume changes." it will conflict with XFCE notifiyd by making duplicate volume notifications); 
12. Separator (Transparent); 
13. Orage Panel Clock. ( In settings, enable check box “Show frame” and replace the text in “Line 1” with %I:%M %p.)

### Shadows
Disable shadows in compositing for an authentic appearance, or at the very least disable “show shadows under dock windows” to prevent dark shading from the panel bar overlapping onto maximized applications.

### Install tweaked icons

For the icon theme, I made a small adjustment that replaces the MS Windows logos with tux penguins. You can install this if you want. To install it, copy the `Chicago95-tux` directory into “/home/$USER/.icons.”

### Notification baloon theme
There is a notification baloon theme with Chicago95.


## Requirements

GTK+ 3.22 or above

Xfce 4.12 of above

(preferred distro is Xubuntu)

### Code and license

License: GPL-3.0+/MIT
