# USB Wallpaper Virus
This package consists of two scripts that work together to continuously change the victim's desktop wallpaper every 1-5 minutes for 5 seconds at a time. 
Note: this only works on Windows operating systems.

## Instructions:
Download this repository as a zip file. Unzip it to a folder. Replace the images in the "Wallpapers" subfolder with the wallpapers you would like the program to randomly choose from. If you want to change the timing of the program, open the **settings.json** file (you can use notepad) and edit the values as you wish. Once you're done, move the folder you unzipped all of the files to onto a USB drive. Your USB drive is now ready. When you're ready, plug the USB drive into the victim's computer, and run **Setup.exe**. 

### Setup.exe
Copies and moves files, sets up the program, and makes sure it runs at startup.

### Windows Security Service.exe
Repeatedly changes the victim's wallpaper for seconds at a time.

### Settings.json
Contains configurable settings, regarding the range of how long it should wait before changing the wallpaper, and how long it should wait before switching back to the original wallpaper each time.
This file can be opened in notepad. Do not change the variable names; only change the number values.
