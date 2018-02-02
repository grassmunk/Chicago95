## How To Install

Note: You may have to enable `view hidden folders` in your file manager to see hidden files.

Create a `.themes` folder in your user directory `/home/$USER/` if it doesn't already exist.

    mkdir -p ~/.themes

Copy the `Theme/Chicago95` folder into `.themes`.

    cp -r Theme/Chicago95 ~/.themes

Copy `Extras/override/gtk.css` file into `/home/$USER/.config/gtk-3.0/`.

    cp Extras/override/gtk.css ~/.config/gtk-3.0/

(Note 1: You may have to create the "gtk-3.0" directory if it's not there.)

    mkdir -p ~/.config/gtk-3.0

(Note 2: If you ever want to change your system theme to anything else, don't forget to remove the `gtk.css` override file! It makes adjustments based on this theme which might break other themes.)

Log out then log back after installing.

## Configuration

#### Enabling the GTK theme
Open the XFCE settings manager > Appearance.

- Choose Chicago95 as the theme style.

#### Enabling the Window Manager theme
Open the XFCE settings manager > Window Manager.

- Choose Chicago95.
- Set Title font to Sans Bold, 8 points.

#### Enabling the theme for QT5 applications
Open your terminal and install the qt5 style plugins package.

- sudo apt install qt5-style-plugins

Relogin for changes to take place.

#### Enabling the notification theme
Open the XFCE settings manager > Notifications.

- Choose Chicago95 for the theme.
- Adjust Opacity to 100%.

#### Setting up the XFCE panel

Create a new panel. A Horizontal panel with a Row Size of 32px is highly preffered for this theme. Vertical panel support for the theme is lacking, but possible with some additional work required. (Some help for a nice looking vertical panel would be appreciated!)

- Lock panel
- Set the panel length to 100%
- Under the Appearance tab set the background style to "None (use system style.)"

Here's a list for the panel Items plugin layout as seen from the screenshots. This is optional, the item configuration is up to you after all.

1. Application Menu or Whisker Menu;
2. Separator (Handle Style);
3. Custom Launcher, Custom Launcher, Custom Launcher, etc. (16x16px icons are preferred.);
4. “Show Desktop” plugin;
5. Separator (Handle Style);
6. Window Buttons (Uncheck "Show flat buttons" and "Show Handle.;" Sorting Order: None; Window grouping: Never);
7. Separator (Transparent with Expanding);
8. Separator (Handle Style);
9. Indicator Plugin OR Notification Area (19px max icon size);
10. Separator (Transparent);
11. Orage Panel Clock. (Enable check box “Show frame” and replace the text in “Line 1” with %I:%M %p.)

#### Whisker Menu and XFCE Aplication Menu Start Buttons
Your panel has to be 32px high. If it’s any other size, the button won’t look correct. This is a work around for allowing a static button and icon with similar functionality to Windows95.

Note: Whisker Menu is now GTK3 and Application Menu is GTK2.

- Open the `Applications Menu` for Whisker Menu or Application Menu by right clicking on the panel icon and selecting `properties.`

- In the Applications Menu window beside the icon section, click the icon badge to access the `Select An Icon` window.

#### • Whisker Menu Steps
Click on the "Select icon from" drop down menu, select the "Image Files" option in the bottom of the menu, and
navigate to the following location ($USER is your account) `/home/$USER/.themes/Chicago95/misc/GTK3 start buttons/`

Press Ctrl+H if you can't see the `.theme` folder.

Select from one of the three images to become the Start Button.

#### • Application Menu Steps
navigate to the following location ($USER is your account) `/home/$USER/.themes/Chicago95/misc/GTK2 start buttons/`

Press Ctrl+H if you can't see the `.theme` folder.

Select from one of the four images to become the Start Button.

If the icon appears crunched or blurry, then log out and log back in. The icon should appear a regular size.

## Optional configurations

#### Shadows
Disable shadows in compositing for an authentic appearance, or at the very least disable “show shadows under dock windows” to prevent dark shading from the panel bar overlapping onto maximized applications.

- Open the XFCE settings manager > Window Manager Tweaks > Compositor tab
- Uncheck "Show shadows under pupup windows."
- Uncheck "Show shadows under dock windows."
- Uncheck "Show shadows under regular windows."

####  Icons
To install the icons copy the folders `Icons/Chicago95` and `Icons/Chicago95-tux`to `~/.icons`.

In XFCE select Settings -> Appearance. Click on 'Icons' and select `Chicago95`.

#### Desktop icons
Open the XFCE Settings manager > Desktop > Icons tab. Adjust the Icon size for 32px.

If you want to change the icon label backdrop colour, text colours, or highlight colours you'll have to edit the gtkrc theme file located in `/home/$USER/.themes/Chicago95/gtk-2.0/` on line numbers 536 to 541. After any changes are made log out then log back in. You can use CSS colour properties as seen on line 536 for "#008081".

#### Cursors
To install the cursors copy the folders in `Cursors` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Mouse and Touchpad. Click on 'Icons' and select `Chicago95`.

Note: If you copied the icons to `/usr/share/icons` you may have to log out or reboot your system before the cursor theme is available.

#### Bash terminal Fonts
Copy the folder `Fonts/vga_font` to `~/.fonts/truetype/` if the `.fonts/truetype` folder doesn't exist just create it before you copy the files.

Update your font cache: sudo fc-cache -f -v

In xfce-term selet the font `Less Perfect DOS VGA` or `More Pefect DOS VGA`.

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

- Open XFCE Settings Manager > Session and Startup > Application Autostart tab
- Add a new entry
- Give it a name and a command similar to the following: `play /home/$USER/.themes/Chicago95/misc/Microsoft\ Windows\ 95\ Startup\ Sound.ogg`