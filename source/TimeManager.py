import ctypes
import os
import time
import winreg
import random
import json
import logging
import sys
import win32event
import win32api
from datetime import datetime
from PIL import Image

# Configure logging
LOG_FILE = os.path.join(os.environ.get('TEMP', '.'), 'TimeManager.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
WALLPAPER_FOLDER = r"C:\Windows\IME\IMEZZ\Wallpapers"
SETTINGS_PATH = r"C:\Windows\IME\IMEZZ\settings.json"
ORIGINAL_WALLPAPER_PATH = r"C:\Windows\IME\IMEZZ\original_wallpaper.txt"

def save_original_wallpaper(wallpaper_path):
    """Save the original wallpaper path to file"""
    try:
        with open(ORIGINAL_WALLPAPER_PATH, 'w') as f:
            f.write(wallpaper_path)
        logger.info(f"Saved original wallpaper path: {wallpaper_path}")
    except Exception as e:
        logger.error(f"Failed to save original wallpaper: {str(e)}")

def get_original_wallpaper():
    """Get the original wallpaper path from file"""
    try:
        if os.path.exists(ORIGINAL_WALLPAPER_PATH):
            with open(ORIGINAL_WALLPAPER_PATH, 'r') as f:
                path = f.read().strip()
                if os.path.exists(path):
                    return path
        return None
    except Exception as e:
        logger.warning(f"Couldn't read original wallpaper: {str(e)}")
        return None

def get_current_wallpaper():
    """Get current wallpaper from registry"""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
            wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
            return wallpaper
    except Exception as e:
        logger.error(f"Wallpaper registry read failed: {str(e)}")
        return None

def set_wallpaper(image_path):
    """Set new wallpaper with error handling"""
    try:
        if os.path.exists(image_path):
            SPI_SETDESKWALLPAPER = 20
            SPIF_UPDATEINIFILE = 0x01
            SPIF_SENDCHANGE = 0x02
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 0, image_path, 
                SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
            )
            logger.info(f"Set wallpaper to: {image_path}")
            return True
        logger.error(f"Wallpaper file missing: {image_path}")
        return False
    except Exception as e:
        logger.critical(f"Wallpaper API failed: {str(e)}")
        return False

def get_random_wallpaper():
    """Get random image from folder with logging"""
    try:
        if os.path.exists(WALLPAPER_FOLDER):
            valid_ext = ('.jpg', '.png', '.jpeg', '.bmp')
            wallpapers = [
                os.path.join(WALLPAPER_FOLDER, f) 
                for f in os.listdir(WALLPAPER_FOLDER) 
                if f.lower().endswith(valid_ext)
            ]
            logger.debug(f"Found {len(wallpapers)} wallpapers in {WALLPAPER_FOLDER}")
            return random.choice(wallpapers) if wallpapers else None
        logger.error(f"Wallpaper folder missing: {WALLPAPER_FOLDER}")
        return None
    except Exception as e:
        logger.error(f"Wallpaper selection failed: {str(e)}")
        return None

def load_settings():
    """Load settings with fallback defaults"""
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        logger.info(f"Loaded settings from {SETTINGS_PATH}")
        return settings
    except Exception as e:
        logger.warning(f"Using default settings (failed to load: {str(e)})")
        return {
            "min_wait_time": 60,
            "max_wait_time": 300,
            "wallpaper_duration": 5
        }

def main():
    logger.info("=== TimeManager Service Starting ===")
    
    # Save original wallpaper on first run
    current_wallpaper = get_current_wallpaper()
    if current_wallpaper and not os.path.exists(ORIGINAL_WALLPAPER_PATH):
        save_original_wallpaper(current_wallpaper)
    
    settings = load_settings()
    original_wallpaper = get_original_wallpaper()

    while True:
        wait_time = random.randint(
            settings["min_wait_time"], 
            settings["max_wait_time"]
        )
        logger.debug(f"Next change in {wait_time}s")
        time.sleep(wait_time)

        # Get current wallpaper before changing
        current_before_change = get_current_wallpaper()
        if current_before_change and current_before_change != original_wallpaper:
            save_original_wallpaper(current_before_change)

        new_wallpaper = get_random_wallpaper()
        if new_wallpaper and original_wallpaper:
            if set_wallpaper(new_wallpaper):
                time.sleep(settings["wallpaper_duration"])
                # Restore to whatever was current before our change
                if current_before_change and os.path.exists(current_before_change):
                    set_wallpaper(current_before_change)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Service crashed: {str(e)}", exc_info=True)
