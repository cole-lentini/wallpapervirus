import ctypes
import os
import time
import winreg
import random
import json
import win32event
import win32api
from PIL import Image

# Constants
WALLPAPER_FOLDER = r"C:\Windows\IME\IMEZZ\Wallpapers"
SETTINGS_PATH = r"C:\Windows\IME\IMEZZ\settings.json"
ORIGINAL_WALLPAPER_PATH = r"C:\Windows\IME\IMEZZ\original_wallpaper.txt"

def save_original_wallpaper(wallpaper_path):
    """Save the original wallpaper path to file"""
    try:
        with open(ORIGINAL_WALLPAPER_PATH, 'w') as f:
            f.write(wallpaper_path)
    except Exception:
        pass

def get_original_wallpaper():
    """Get the original wallpaper path from file"""
    try:
        if os.path.exists(ORIGINAL_WALLPAPER_PATH):
            with open(ORIGINAL_WALLPAPER_PATH, 'r') as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
        return None
    except Exception:
        return None

def get_current_wallpaper():
    """Get current wallpaper from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
            return winreg.QueryValueEx(key, "WallPaper")[0]
    except Exception:
        return None

def set_wallpaper(image_path):
    """Set new wallpaper with error handling"""
    try:
        if os.path.exists(image_path):
            ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
            return True
        return False
    except Exception:
        return False

def get_random_wallpaper():
    """Get random image from folder"""
    try:
        if os.path.exists(WALLPAPER_FOLDER):
            valid_ext = ('.jpg', '.png', '.jpeg', '.bmp')
            wallpapers = [
                os.path.join(WALLPAPER_FOLDER, f) 
                for f in os.listdir(WALLPAPER_FOLDER) 
                if f.lower().endswith(valid_ext)
            ]
            return random.choice(wallpapers) if wallpapers else None
        return None
    except Exception:
        return None

def load_settings():
    """Load settings with fallback defaults"""
    try:
        with open(SETTINGS_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {
            "min_wait_time": 60,
            "max_wait_time": 300,
            "wallpaper_duration": 5
        }

def main():
    # Save original wallpaper on first run
    current_wallpaper = get_current_wallpaper()
    if current_wallpaper and not os.path.exists(ORIGINAL_WALLPAPER_PATH):
        save_original_wallpaper(current_wallpaper)
    
    settings = load_settings()
    original_wallpaper = get_original_wallpaper()

    while True:
        time.sleep(random.randint(
            settings["min_wait_time"], 
            settings["max_wait_time"]
        ))

        current_before_change = get_current_wallpaper()
        if current_before_change and current_before_change != original_wallpaper:
            save_original_wallpaper(current_before_change)

        new_wallpaper = get_random_wallpaper()
        if new_wallpaper and original_wallpaper:
            if set_wallpaper(new_wallpaper):
                time.sleep(settings["wallpaper_duration"])
                if current_before_change and os.path.exists(current_before_change):
                    set_wallpaper(current_before_change)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
