## Plymouth Chicago95 Theme

This theme is based on the template provided by http://brej.org/blog/?p=174

It is meant to simulate the Windows 95 boot screen and shutdown screen.

to install (Ubuntu):

sudo cp -r Chicago95 /lib/plymouth/themes/
sudo update-alternatives --install /lib/plymouth/themes/default.plymouth default.plymouth /lib/plymouth/themes/Chicago95/Chicago95.plymouth 100
sudo update-alternatives --config default.plymouth  #here, choose the number of the theme you want to use then hit enter
sudo update-initramfs -u
