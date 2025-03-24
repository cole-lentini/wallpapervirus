import ctypes
import os
import time
import winreg
import random
import json

# Load settings from a JSON file
CONFIG_FILE = "settings.json"
def load_settings():
    """Load settings from the JSON config file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {"min_wait_time": 60, "max_wait_time": 300, "wallpaper_duration": 5}  # Default values

settings = load_settings()
MIN_WAIT_TIME = settings["min_wait_time"]
MAX_WAIT_TIME = settings["max_wait_time"]
WALLPAPER_DURATION = settings["wallpaper_duration"]

def get_current_wallpaper():
    """Retrieve the current desktop wallpaper from Windows registry."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
            wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
        return wallpaper
    except Exception:
        return None

def set_wallpaper(image_path):
    """Set the desktop wallpaper using Windows API."""
    try:
        if os.path.exists(image_path):
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE)
    except Exception:
        pass

def get_random_wallpaper(folder_path):
    """Select a random wallpaper from the given folder."""
    try:
        if os.path.exists(folder_path):
            wallpapers = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp'))]
            if wallpapers:
                return random.choice(wallpapers)
    except Exception as e:
        print(f"Error selecting wallpaper: {e}")
    return None

# Path to the Wallpapers folder
wallpaper_folder = r"C:\ProgramData\SystemAssets\Wallpapers"

# Get the current wallpaper
original_wallpaper = get_current_wallpaper()

# Infinitely repeat script
while True:
    # Wait for a random time within the set range
    wait_time = random.randint(MIN_WAIT_TIME, MAX_WAIT_TIME)
    print(f"Waiting {wait_time} seconds before changing wallpaper...")
    time.sleep(wait_time)
    
    if original_wallpaper:
        # Pick a random wallpaper from the folder
        new_wallpaper = get_random_wallpaper(wallpaper_folder)
        
        if new_wallpaper:
            # Change wallpaper to the new image
            set_wallpaper(new_wallpaper)
            print(f"Changed wallpaper to {new_wallpaper}")

            # Wait for the configured duration
            print(f"Displaying new wallpaper for {WALLPAPER_DURATION} seconds...")
            time.sleep(WALLPAPER_DURATION)

            # Revert to the original wallpaper
            set_wallpaper(original_wallpaper)
            print("Reverted to original wallpaper.")
        else:
            print("No wallpapers found in the folder.")
