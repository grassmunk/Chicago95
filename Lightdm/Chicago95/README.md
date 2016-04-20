paddy-greeter
========

Paddy-Greeter is a greeter(read: a login screen) for use with lightdm and lightdm-webkit-greeter.

It has pretty limited functionality, but looks pretty neat.
A screenshot of paddy-greeter in action can be found [here](https://raw.github.com/kalmanolah/paddy-greeter/master/screenshot.png).

![paddy-greeter](https://raw.github.com/kalmanolah/paddy-greeter/master/screenshot.png)


It's called paddy because it's full of rice. It's a terrible pun and I feel like a bad person for finding it funny.

Documentation
-------------

You'll need to have lightdm and lightdm-webkit for this to work. On Debian-based systems, you'd do something like:

    sudo apt-get install lightdm lightdm-webkit-greeter

First, configure lightdm to use lightdm-webkit-greeter if you haven't already. To do so, open up `/etc/lightdm/lightdm.conf` with vim or whatever and change it to something like this:

    [SeatDefaults]
    greeter-session=lightdm-webkit-greeter
    user-session=<Your XSession filename goes here (without .desktop)>
    allow-guest=<TRUE | FALSE - Enable the guest account?>

A properly configured `/etc/lightdm/lightdm.conf` would look something like this:

    [SeatDefaults]
    greeter-session=lightdm-webkit-greeter
    user-session=gnome-awesome
    allow-guest=false

Next, configure lightdm-webkit-greeter to use paddy-greeter. You can do so by editing `/etc/lightdm/lightdm-webkit-greeter.conf` and setting `theme-name`to `paddy`:

    #
    # background = Background file to use, either an image path or a color (e.g. #772953)
    # theme-name = GTK+ theme to use
    # font-name = Font to use
    # xft-antialias = Whether to antialias Xft fonts (true or false)
    # xft-dpi = Resolution for Xft in dots per inch (e.g. 96)
    # xft-hintstyle = What degree of hinting to use (hintnone, hintslight, hintmedium, or hintfull)
    # xft-rgba = Type of subpixel antialiasing (none, rgb, bgr, vrgb or vbgr)
    #
    [greeter]
    theme-name=Ambiance
    webkit-theme=paddy
    font-name=Ubuntu 11
    xft-antialias=true
    xft-dpi=96
    xft-hintstyle=slight
    xft-rgba=rgb

Finally, clone the repo and copy the folder to the lightdm-webkit themes directory.

    git clone git://github.com/kalmanolah/paddy-greeter.git
    sudo cp -R paddy-greeter /usr/share/lightdm-webkit/themes/paddy

OPTIONAL: Change the distro image to something else, as I currently don't have a way to determine your distro. Open up `js/main.js` and change `distro_image` to a distro logo of your choosing. It should correspond to `img/distro/<distro_image>`.

    distro_image = 'ubuntu.svg'; // distro image is 'img/distro/ubuntu.svg'

Dependencies
------------

lightdm, lightdm-webkit-greeter and a brain

License
-------

This greeter is MIT-licensed, but few people care. Check out the LICENSE file if you think you've got what it takes.

Credits
-------

This theme uses some third party resources to bring you its deliciousness. All of the resources used belong to their respective owners and creators and stuff.

Some of the stuff used:

*   [Navaho](http://www.colourlovers.com/pattern/465753/Navaho) by [miice](http://www.colourlovers.com/lover/miice)
*   [Fabric of Squares](http://subtlepatterns.com/fabric-of-squares/) by [Heliodor Jalba](http://about.me/heliodor)
*   [Normalize.css](http://necolas.github.io/normalize.css/) by [Nicolas Gallagher](http://nicolasgallagher.com/)
*   [Iconic](http://www.somerandomdude.com/work/iconic/) by [P.J. Onori](http://www.somerandomdude.com/)
*   [Ostrich Sans](http://www.theleagueofmoveabletype.com/ostrich-sans) by [Tyler Finck](http://www.theleagueofmoveabletype.com/members/sursly) and [The League of Moveable Type](http://www.theleagueofmoveabletype.com/)
*   [mock.js](https://github.com/Wattos/LightDM-Webkit-MacOSX-Theme/blob/master/mock.js) from the [LightDM Webkit MacOSX Theme](https://github.com/Wattos/LightDM-Webkit-MacOSX-Theme) by [Wattos](https://github.com/Wattos)
