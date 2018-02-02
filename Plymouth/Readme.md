## Plymouth boot splash theme

The Windows95 boot theme is based on the template provided by http://brej.org/blog/?p=174

It is meant to simulate the Windows 95 boot screen and shutdown screen.

The RetroTux boot theme is based on the xubuntu-logo Plymouth theme.

#### Install instructions for XUbuntu
Copy the theme folder into the Plymouth theme directory.

- `sudo cp -r Chicago95/Plymouth/Chicago95 /usr/share/plymouth/themes/`
- `sudo cp -r Chicago95/Plymouth/RetroTux /usr/share/plymouth/themes/`

Add to default.plymouth

- `sudo update-alternatives --install /usr/share//plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/Chicago95/Chicago95.plymouth 100`
- `sudo update-alternatives --install /usr/share//plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/RetroTux/RetroTux.plymouth 100`

Choose the theme to load. (As you run the following command there will be a number assigned to each theme and located in the first column of a list. Use that number to specify the theme and press enter to continue.)

- `sudo update-alternatives --config default.plymouth`

Update initramfs

- `sudo update-initramfs -u`
