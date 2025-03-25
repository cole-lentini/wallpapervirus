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
import win32service
import win32serviceutil
import servicemanager
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
SERVICE_NAME = "W32TimeManager"

def load_settings():
    """Load settings with validation"""
    defaults = {
        "min_wait_time": 60,
        "max_wait_time": 300,
        "wallpaper_duration": 30,
        "wait_until_restart_to_run": False
    }
    
    try:
        with open(SETTINGS_PATH, 'r') as f:
            settings = json.load(f)
        # Validate values
        settings["min_wait_time"] = max(1, int(settings.get("min_wait_time", 60)))
        settings["max_wait_time"] = max(settings["min_wait_time"], int(settings.get("max_wait_time", 300)))
        settings["wallpaper_duration"] = max(1, int(settings.get("wallpaper_duration", 30)))
        logger.info(f"Loaded settings: {settings}")
        return settings
    except Exception as e:
        logger.warning(f"Using defaults: {str(e)}")
        return defaults

def get_wallpapers():
    """Get valid wallpapers from folder"""
    if not os.path.exists(WALLPAPER_FOLDER):
        logger.error(f"Wallpaper folder missing: {WALLPAPER_FOLDER}")
        return []
    
    valid_files = []
    for f in os.listdir(WALLPAPER_FOLDER):
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            img_path = os.path.join(WALLPAPER_FOLDER, f)
            try:
                Image.open(img_path).verify()
                valid_files.append(img_path)
            except Exception as e:
                logger.warning(f"Invalid image {f}: {str(e)}")
    
    return valid_files

def set_wallpaper(image_path):
    """Set wallpaper with retries"""
    SPI_SETDESKWALLPAPER = 0x0014
    for attempt in range(3):
        try:
            if ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3):
                return True
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return False

def main():
    """Main application logic"""
    # Single instance check
    mutex = win32event.CreateMutex(None, False, "Global\\TimeManagerMutex")
    try:
        if win32event.WaitForSingleObject(mutex, 0) != win32event.WAIT_OBJECT_0:
            logger.error("Another instance is running")
            return

        logger.info("=== TimeManager Started ===")
        settings = load_settings()
        wallpapers = get_wallpapers()
        
        if not wallpapers:
            logger.error("No valid wallpapers found")
            return

        # Get current wallpaper
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                current_wallpaper, _ = winreg.QueryValueEx(key, "WallPaper")
            logger.info(f"Current wallpaper: {current_wallpaper}")
        except Exception as e:
            current_wallpaper = None
            logger.warning(f"Couldn't read current wallpaper: {str(e)}")

        # Main loop
        while True:
            wait_time = random.randint(
                settings["min_wait_time"],
                settings["max_wait_time"]
            )
            logger.info(f"Waiting {wait_time} seconds")
            time.sleep(wait_time)

            new_wallpaper = random.choice(wallpapers)
            logger.info(f"Changing to: {new_wallpaper}")
            
            if set_wallpaper(new_wallpaper):
                time.sleep(settings["wallpaper_duration"])
                if current_wallpaper and os.path.exists(current_wallpaper):
                    set_wallpaper(current_wallpaper)

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        if mutex:
            win32api.CloseHandle(mutex)

class TimeService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = "Windows Time Management"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.is_running = True
        main()

def run_as_service():
    """Service entry point with proper initialization"""
    try:
        # Give service manager time to initialize
        time.sleep(10)
        
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TimeService)
        servicemanager.StartServiceCtrlDispatcher()
    except Exception as e:
        logger.critical(f"Service initialization failed: {str(e)}", exc_info=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--service':
        run_as_service()
    else:
        # Run as regular application
        main()
