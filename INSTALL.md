# Install Guide

[Installing The Theme](#install_theme)

[Configuring The Theme](#config_theme)

[Configuring The XFCE4 Panelbar](#xfce4_panel)

[Start Buttons](#start_buttons)

[Additional Enhancements](#add_enhance)

---
<a name="install_theme"/>

## Installing Chicago95

The following installation steps will require that you enable the `view hidden folders` option in your file manager to see hidden files.

#### Step 1: Prepare theme and icon directories

Create a `.themes` folder in your user directory `/home/$USER/` if it doesn't already exist. (with $USER being your username.)

    mkdir -p ~/.themes

Create a `.icons` folder in your user directory `/home/$USER/` if it doesn't already exist.

    mkdir -p ~/.icons

#### Step 2: Copy the Chicago95 GTK and icon themes

Copy the GTK theme from `Chicago95-master/Theme/` folder into `.themes`.

    cp -r Chicago95-master/Theme/Chicago95 ~/.themes

Copy the icon themes from `Chicago95-master/Icons/` folder into `.icons`.

    cp -r Chicago95-master/Icons/* ~/.icons

Copy the GTK3 CSS override file from `Chicago95-master/Extras/override/` into `/home/$USER/.config/gtk-3.0/`.

    cp Chicago95-master/Extras/override/gtk.css ~/.config/gtk-3.0/

(Note 1: You may have to create the "gtk-3.0" directory if it's not there.)

    mkdir -p ~/.config/gtk-3.0

(Note 2: If you ever want to change your system theme to anything else, don't forget to remove the `gtk.css` override file! It makes adjustments based on this theme which might break other themes.)

#### Step 3:

After copying the theme files into their appropriate places, you might need to log out then log back in for any changes to take places.

---
<a name="config_theme"/>

## Configuring Chicago95

The following steps will guide you through enabling the theme and making additional configurations if desired.

#### Enabling the GTK theme
- Open the XFCE settings manager > Appearance.
- Choose Chicago95 as the theme style.

#### Enable the icon theme
- Open the XFCE settings manager > Appearance > Icons.
- Select Chicago95 or Chicago95-tux.

#### Enabling the Window Manager theme
- Open the XFCE settings manager > Window Manager.
- Choose Chicago95 as the theme style.
- Set Title font to Sans Bold, 8 points.

#### Enabling the theme for QT5 applications (optional)
For QT5 applications such as KeePassXC or q4-Wine, you can enable GTK theme support.  This can improve theme consistency across a range of applications.  Chicago95 on QT5 applications works quite well, however there might occasionally be a few small bugs; one example being scrollbox buttons missing their borders.

To begin setting this up install the qt5 style plugins package.

    sudo apt install qt5-style-plugins

After the installation is complete, relogin for changes to take place.

For further tuning of QT5 with the Chicago95 GTK theme, read [QT5 theme configration with qt5ct](#config_qt5ct)

#### Enabling the notification theme
- Open the XFCE settings manager > Notifications.
- Choose Chicago95 for the theme.
- Adjust Opacity to 100%.


---
<a name="xfce4_panel"/>

## Configuring The XFCE4 Panelbar

The following steps will guide you through configuring the XFCE4 panelbar to resemble as closeley as possible the taskbar seen in MS Windows95. This won't appear 1-to-1, but it can point you in the right direction.

#### Step 1: Setting the panelbar size
The following steps assume that the panelbar will be horizontal; seen on the top or bottom of your display.

- Open the XFCE settings manager > Panel
- From the Display tab set the panel mode to "Horizontal."
- Check "Lock Panel."
- Row Size (pixels): Set to 24px; Unless you want to use a different row size. If you choose to use a different row size, make note that even numbers for the Row Size slider are recommended (odd number row sizes will cause icon scaling issues.)
- Under the Appearance tab set the background style to "None (use system style.)"

#### Step 2: Adding panelbar plugins
Open the XFCE settings manager > Panel > Items

Here's an organized list for the panel Items plugin layout.

1. Application Menu or Whisker Menu;
2. Separator (Handle Style);
3. Custom Launcher, Custom Launcher, Custom Launcher, etc;
4. “Show Desktop” plugin;
5. Separator (Handle Style);
6. Window Buttons (Uncheck "Show flat buttons" and "Show Handle.;" Sorting Order: None; Window grouping: Never);
7. Separator (Transparent with Expanding enabled);
8. Separator (Handle Style);
9. Indicator Plugin OR Notification Area (19px max icon size preferred; also uncheck "Show frame");
10. Orage Panel Clock. (Enable check box “Show frame” and replace the text in “Line 1” with %I:%M %p.)

---
<a name="start_buttons"/>

## Start Buttons

The following steps will guide you through setting up an MS Windows 95 themed "Start" button.

Something to keep in mind, the Whisker Menu plugin is now GTK3 since XUbuntu 17.10 and Debian Buster. The Application Menu plugin is still GTK2. This can differ for other distributions.

#### • Whisker Menu
Open the XFCE settings manager > Panel > Items tab > Double click the Whisker menu item in the item list.

- In the whisker properties menu click the icon option.
- In the icon select window navigate to `/home/$USER/.themes/Chicago95/misc` (with $USER being your username.)

`misc/` contains simple small icons badges in two sizes. (32x32px icons are ideal for larger panelbars)

`Legacy GTK3 start buttons/` contains start buttons that were used for an older version of the Whisker Menu plugin.

Note: The smallest optimal panel row size for this theme is 24 pixels. If your panel is below that size, you will encounter icon scaling issues.

#### • Application Menu
Open the XFCE settings manager > Panel > Items tab > Double click the Applications Menu item in the item list.

- In the Applications properties menu click the icon option.
- In the icon select window navigate to `/home/$USER/.themes/Chicago95/misc/GTK2 start buttons` (with $USER being your username.)

Since the Application Menu plugin is still GTK2, you'll have to choose an icon associated with your panel size. For example, tux_32px.png would be ideal on a panel with a row size of 32 pixels.

Note: The smallest optimal panel row size for this theme is 24 pixels. If your panel is below that size, you will encounter icon scaling issues.

---
<a name="add_enhance"/>

## Additional Enhancements

This section of the guide contains additional enchancements that can be made to improve the theme. These are all optional and might require some advanced knowledge of operating your system.

#### Launcher Button icon scaling (advanced)
This might be a little complicated since it's more of a work-around than a good solution. I tried making this as simple as possible where you can just adjust configurations in a file. If there are questions or issues with the following instructions, open a ticket and i'll try to walk you through it.

If you want to force 16x16px icons in the launcher buttons, you can do this through the theme by editing the panel.rc file where there are commented options for icon scales.

- Open a text editor and navigate to `/home/$USER/.themes/Chicago95/gtk-2.0/panel.rc` (with $USER being your username.)
- Move to line 250 of the file where you will see a section specified for Launcher buttons.

Example steps: You will first need to determine your current panel bar row size since the launcher button icon padding is determined by the vertical size of the panel bar.

- Open the XFCE settings manager > Panel
- Verify the "Row Size (pixels)". (Lets say that it's 38 pixels for this example.)
- Return back to the text editor and locate the line comment that is specifying your panel bar row size. (38px height panel for this example is on line 284.)
- Delete the "#" pound comment character in front of the xthickness and the ythickness values for the specified panel bar size.
- Now Insert a "#" pound comment character in front of the xthickness and the ythickness values of the previous default selection, which is for a 24px height panel.
- Save the file and reload the xfce panel bar. You can run `xfce4-panel -r` in a terminal to reload the panel.

Note: Even numbered panel bar row sizes seem to work best. If your panel bar row size is "29px" for example, the launcher icons may not scale correctly.

If you use a vertical deskbar, you could add a second row from the panel properties menu to organize the launcher buttons into rows. This would have a more organized effect.

<a name="config_qt5ct"/>

#### QT5 theme configration with qt5ct (advanced)

The following steps are written from the XUbuntu desktop. These will vary on other distributions.

You can use qt5ct for further modifying qt5 application themes to resemble the GTK theme. To set this up you can install qt5ct.

    sudo apt install qt5ct

After installing qt5ct you will have to configure an environment variable so that the QT platform theme calls on qt5ct and not GTK.

- Open a text editor as root or sudo elevation and navigate to `/etc/X11/Xsession.d/56xubuntu-session` (Note: 56xubuntu-session may be a different name if you are on a different distribution.)
- There will be a line with the following "# QT5 apps to use GTK style" and below that the variable `export QT_QPA_PLATFORMTHEME=gtk2`
- Change the variable to `export QT_QPA_PLATFORMTHEME=qt5ct`
- Save changes made, then log out and log back into your system.

Once you are logged back into your desktop you can access Qt5 Settings.

- In the QT5 Settings window adjust the style dropdown to GTK2.
- In the Icon Theme tab you can select the Chicago95 icon theme here.
- Click "Apply" to apply adjustments and OK to finish.

#### Shadow effects
Disable shadows in compositing for an authentic appearance, or at the very least disable “show shadows under dock windows” to prevent dark shading from the panel bar overlapping onto maximized applications.

- Open the XFCE settings manager > Window Manager Tweaks > Compositor tab
- Uncheck "Show shadows under pupup windows."
- Uncheck "Show shadows under dock windows."
- Uncheck "Show shadows under regular windows."

#### GTK Overlay Scrollbars
Note: You may have to enable `view hidden folders` in your file manager to see hidden files.

GTK Overlay Scrollbars can be disabled from the `.xsessionrc` file located in the `Chicago95-master/Extras/override` folder.

Copy the .xsessionrc file into your user directory `/home/$USER/` or append the contents if you already have a .xsessionrc file.

Log out then log back in.

#### Desktop background color
If you want to use the default Windows 95 gray instead of a background image, right click the desktop and select Desktop Settings.  On the Background tab, set "Color" to "Solid color", and for the first color picker set "Color name" to #008080.  Disable the background image by setting "Style" to "None".

#### Desktop icons (text shadows and label backdrop )(advanced)
If you want to change the icon label backdrop colour, text colours, or highlight colours you'll have to edit the gtkrc theme file located in `/home/$USER/.themes/Chicago95/gtk-2.0/`.

Text shadows can be modified from lines 553 to 559. These are currently commented out with "#."

Label backdrop colours can be modified on line numbers 565 to 570.

After any changes are made log out then log back in. You can use CSS colour properties as seen on line 551 for any colour you want.

#### Cursors
To install the cursors copy the folders in `Cursors` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Mouse and Touchpad. Click on 'Icons' and select `Chicago95`.

Note: If you copied the icons to `/usr/share/icons` you may have to log out or reboot your system before the cursor theme is available.

#### MS Sans Serif font
For an authentic Windows 95 feel, you can use the original MS Sans Serif font.  Create a directory called `ms_sans_serif` inside `~/.fonts/truetype/`, and copy over to this directory the C:\Windows\Fonts\micross.ttf file from any modern Windows computer (this font is titled "Microsoft Sans Serif Regular"). Update the font cache by running `sudo fc-cache -f -v`.

To set the main font for the entire system, open the XFCE settings manager > Appearance > Fonts tab.  Set the "Default font" to Microsoft Sans Serif, style Regular, size 8.

**NOTE: This step will affect font rendering for the entire system.  Only apply these settings if you truly want an authentic Windows 95 look and feel.** In the "Rendering" section of the Fonts tab, uncheck "Enable anti-aliasing", and set "Hinting" to any value except None. Set the sub-pixel order as desired.

To set the title bar font, open the XFCE settings manager > Window Manager > Style tab.  Set the "Title font" to Microsoft Sans Serif, style Regular, size 8.

Finally, set the font for the Orage panel clock by right-clicking the panel clock, selecting Properties, then next to Line 1, change the font to Microsoft Sans Serif, style Regular, size 8.  Inside the Line 1 box, add two spaces before and after the value in the box, to apply some spacing.

#### Bash terminal Fonts
Copy the folder `Fonts/vga_font` to `~/.fonts/truetype/` if the `.fonts/truetype` folder doesn't exist just create it before you copy the files.

Update your font cache: `sudo fc-cache -f -v`

In xfce-term select the font `Less Perfect DOS VGA` or `More Pefect DOS VGA`, size 12.  For better readability, uncheck "Allow bold text".

[Click here](https://int10h.org/oldschool-pc-fonts/fontlist/) for more classic fonts.

#### Bash terminal MS-DOS theme
Copy the file `Extras/Chicago95.theme` to `~/.local/share/xfce4/terminal/colorschemes` (create the colorschemes folder if it doesn't exist: `mkdir .local/share/xfce4/terminal`).
Under preferences in xfce-term select 'Colors.' Under `Presets` you should see `Chicago 95`.

To get the MS-DOS `C:\>` prompt and startup message add the contents of `Extras/DOSrc` to your `.bashrc` file: `cat Extras/DOSrc >> ~/.bashrc`.
To get MS-DOS Prompt title, go to the Preferences prompt and change title to MS-DOS Prompt and select isn't displayed on The Dynamically-Set Title

#### oh-my-zsh MS-DOS theme
Copy the file `Extras/Chicago95.zsh-theme` to `~/.oh-my-zsh/themes` (if you have changed your `.oh-my-zsh` config location, put the theme in that folder). In your `.zshrc` change your theme to Chicago95.

This will add the MS-DOS prompt. You will get a C prompt by default. If the previous command had an exit code other than 0 you will get an F prompt. If you are in a git repository you will git a G prompt, followed by the branch (in yellow) and the status (clean in green, dirty in red).

To get the startup message, add the contents of `Extras/ZSHDOSrc` to your `.zshrc` file: `cat Extras/ZSHDOSrc >> ~/.zshrc`.

#### Windows 95 login startup sound
Copy the file `Extras/Microsoft Windows 95 Startup Sound.ogg` to `/home/$USER/.themes/Chicago95/misc/Microsoft Windows 95 Startup Sound.ogg` or where ever you want.

##### XFCE
- Open XFCE Settings Manager > Session and Startup > Application Autostart tab
- Add a new entry
- Give it a name and a command similar to the following: `play /home/$USER/.themes/Chicago95/misc/Microsoft\ Windows\ 95\ Startup\ Sound.ogg`

##### LXDE
- Create the file `./config/autostart/chicago95.desktop` with the following contents:

```
[Desktop Entry]
Type=Application
Name=Chicago95 Chime
Comment=The Windows 95 startup sound
Exec=sh -c 'play /home/$HOME/.themes/Chicago95/misc/Microsoft\ Windows\ 95\ Startup\ Sound.ogg'
OnlyShowIn=LXDE
```

---
<a name="hidpi"/>

## HiDPI

There is only partial HiDPI support but it works pretty well

#### Appearance settings

- Increase DPI from 96 to 192
- *(Optional)* Increase default font from Sans 8 to Sans 9

#### Replace xfwm4 theme with HiDPI version

Use HiDPI theme

    mv ~/.themes/Chicago95/xfwm4 ~/.themes/Chicago95/xfwm4_lodpi
    mv ~/.themes/Chicago95/xfwm4_hidpi ~/.themes/Chicago95/xfwm4

#### Replace configs with HiDPI version

Make GTK2 buttons bigger

    sed -i 's/#include "button.rc"/include "button.rc"/' ~/.themes/Chicago95/gtk-2.0/gtkrc

Increase taskbar size

    cp ~/.gtkrc-2.0 ~/.gtkrc-2.0.bak
    cp Chicago95-master/Extras/hidpi/.gtkrc-2.0 ~/.gtkrc-2.0

#### Adjust settings for HiDPI

Make GTK icons bigger

    xfconf-query -c xsettings -p /Gtk/IconSizes -s "gtk-large-toolbar=32,32:gtk-small-toolbar=24,24:gtk-menu=32,32:gtk-dialog=88,88:gtk-button=32,32:gtk-dnd=32,32"

Increase icon size in Thunar File Manager

    xfconf-query -c thunar -p /shortcuts-icon-size -s "THUNAR_ICON_SIZE_SMALL"
    xfconf-query -c thunar -p /tree-icon-size -s "THUNAR_ICON_SIZE_SMALLER"

Increase icon size on desktop

    xfconf-query -c xfce4-desktop -p /desktop-icons/icon-size -s 64

#### Cursors

The cursors in the theme do not support HiDPI but [Hackneyed](https://www.gnome-look.org/p/999998/startdownload?file_id=1549578280&file_name=Hackneyed-48px-0.7.2-right-handed.tar.bz2&file_type=application/x-bzip2&file_size=49921) is a good alternative. Download and extract to `~/.icons` and select it in Mouse settings.

#### Panelbar tweaks

- Set panel row size to 48
- Application Menu: Check show button title and set it to 𝗦𝘁𝗮𝗿𝘁 (copy+paste)
- Notification Area: Set maximum icon size to 32
- Indicator Plugin: Check square icons
- Status Notifier Plugin: Set maximum icon size to 32
- *(Optional)* Orage Panel Clock: Set width to 144 and font to Sans 9
