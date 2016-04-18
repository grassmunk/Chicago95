# Chicago95

## XFCE / Xubuntu Windows 95 Total Conversion

I was unhappy with the various XFCE/GTK2/GTK3 Windows 95 based themes and decided to make one that was more consistent accross the board for theming.

Included in this theme:

- New icons to complete the icon theme started with Classic95
- Edited Redmond XFWM theme to more accurately reflect Windows 95
- Edited Xfce-Redmond by dbbolton to be more accurate and include XFCE panels
- Created GTK-3.0 theme from scratch (based on Win 10 and Mate themes)
- Plymouth theme created from scratch

## Screenshots
![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/plymouth.png "Plymouth")

![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/lightdm.png "LightDM")

![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/Screenshot.png "Big Screenshot")

![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/gtk2.png "GTK2")

![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/gtk3.png "GTK3")

I decided that the pop-overs were almost exactly as annoying/ugly as Clippy was in MS Office 97 so the buttons/coloring are matched to look exactly like that.

![alt text](https://raw.githubusercontent.com/grassmunk/Chicago95/master/Screenshots/DOS.png "Terminal")

## Installation

### Themes
Copy the folder `Theme/Chicago95` to the themes directory i.e. `/usr/share/themes/` or `~/.themes`.

In XFCE select Settings -> Appearance. Click on 'Style' and select `Chicago95`.

For window borders select Settings -> Window Manager. Under 'Style' select `Chicago 95`.

Background: Just set to whatever you like, for a more authentic look try setting Style to none and color to `#008080`.

###  Icons
To install the icons copy the folder `Icons/Chicago95` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Appearance. Click on 'Icons' and select `Chicago95`.

### Cursors
To install the cursors copy the folders in `Cursors` to `/usr/share/icons` or `~/.icons`.

In XFCE select Settings -> Mouse and Touchpad. Click on 'Icons' and select `Chicago95`.

### Fonts
Copy the folder `Fonts/vga_font` to `~/.fonts/truetype/` if the `.fonts/truetype` folder doesn't exist just create it before you copy the files. 

Update your font cache: sudo fc-cache -f -v

In xfce-term selet the font `Less Perfect DOS VGA` or `More Pefect DOS VGA`.

### Terminal

Copy the file `Extras/Chicago95.theme` to `~/.local/share/xfce4/terminal/colorschemes` (create the colorschemes folder if it doesn't exist: `mkdir .local/share/xfce4/terminal`).
Under preferences in xfce-term select 'Colors.' Under `Presets` you should see `Chicago 95`.

To get the MS-DOS `C:\>` prompt and startup message add the contents of `Extras/DOSrc` to your `.bashrc` file: `cat Extras/DOSrc >> ~/.bashrc`.

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

## Requirements

GTK+ 3.16 or above

Xfce 4.12 of above

(preferred distro is Xubuntu)

### Code and license

License: GPL-3.0+/MIT
