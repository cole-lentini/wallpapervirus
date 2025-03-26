# USB Wallpaper Virus
This package consists of scripts that work together to continuously change the victim's desktop wallpaper every 1-5 minutes for 5 seconds at a time. 
_**Note: this only works on Windows operating systems.**_

## ⚠️IMPORTANT⚠️
To ensure the program works properly, do not modify any files, with two exceptions: 
1. You may rename, delete, replace, or add image files to the [**"Wallpapers" folder**](#wallpapers-folder).
2. You may change the number or boolean values inside [**Settings.json**](#settingsjson).

## Instructions:
1. Download everything in the [**build folder**](#build-folder) as a zip file, and unzip it to a folder.
2. Replace the images in the [**"Wallpapers" subfolder**](#wallpapers-folder) with the wallpapers you would like the program to randomly choose from.
3. If you want to change the program settings, open the [**Settings.json**](#settingsjson) file (you can use notepad) and edit the values as you wish.
4. Move the unzipped folder onto your USB drive. Your USB drive is now set up properly.

Keep in mind, **once set up, the USB drive is infinitely reuseable** for spreading the USB Wallpaper Virus.

5. Plug the USB drive into the victim's computer.
6. Open the USB drive in file explorer.
7. Right click and run [**Setup.exe**](#setupexe) as administrator.
8. Wait for 5-10 seconds, until a popup box appears, which should say that the installation was a success.
9. Remove the USB drive. 

Your victim's computer is now infected with the USB Wallpaper Virus.
If you ever wish to change/add more wallpapers for the program to choose from, or change the virus's settings, after already having installed the virus to the victim's computer, simply make the desired changes on the USB drive (by changing/adding more wallpapers to the [**"Wallpapers" folder**](#wallpapers-folder) and/or editing [**Settings.json**](#settingsjson)), and then repeat steps 5-9 above. Every time you run [**Setup.exe**](#setupexe), it will update the settings of the existing virus files on the victim's computer.

## build folder
Contains the following project files:
### [Setup.exe](../main/build/Setup.exe)
Copies and moves files, sets up the virus, and makes sure it runs at startup.

### [TimeManager.exe](../main/build/TimeManager.exe)
Repeatedly changes the victim's wallpaper for seconds at a time.

### [Settings.json](../main/build/Settings.json)
Contains configurable settings, regarding the range of how long it should wait before changing the wallpaper, how long it should wait before switching back to the original wallpaper each time, and whether or not the virus should wait to run until the victim restarts their computer. 

### [Wallpapers Folder](../main/build/Wallpapers)
Contains wallpapers you would like the virus to randomly choose from.

## source folder
Contains the following source files:
### [Setup.py](../main/source/Setup.py)
Used to create [**Setup.exe**](#setupexe)
### [TimeManager.py](../main/source/TimeManager.py)
Used to create [**TimeManager.exe**](#timemanagerexe)
