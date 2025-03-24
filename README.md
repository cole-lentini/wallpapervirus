# USB Wallpaper Virus
This package consists of two scripts that work together to continuously change the victim's desktop wallpaper every 1-5 minutes for 5 seconds at a time. 
__Note: this only works on Windows operating systems.__

## Instructions:
1. Download this repository as a zip file, and unzip it to a folder.
2. Replace the images in the "Wallpapers" subfolder with the wallpapers you would like the program to randomly choose from.
3. If you want to change the timing of the program, open the **settings.json** file (you can use notepad) and edit the values as you wish.
4. Move the unzipped folder onto your USB drive. Your USB drive is now set up properly.

   Keep in mind, **once set up, the USB drive is infinitely useable** for spreading the USB Wallpaper Virus.
   
5. Plug the USB drive into the victim's computer.
6. Open the USB drive in file explorer.
7. Right click and run **Setup.exe** as administrator.
8. Wait 5-10 seconds, then remove the USB drive.

Your victim's computer is now infected with the USB Wallpaper Virus.

## Files
### Setup.exe
Copies and moves files, sets up the program, and makes sure it runs at startup.

### Windows Security Service.exe
Repeatedly changes the victim's wallpaper for seconds at a time. Do not change the name of this file. 

### Settings.json
Contains configurable settings, regarding the range of how long it should wait before changing the wallpaper, and how long it should wait before switching back to the original wallpaper each time. Do not change the variable names; only change the number values.
