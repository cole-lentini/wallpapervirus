import os
import shutil
import sys
import json
import subprocess
import logging
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import win32api
import win32con
import ctypes
from datetime import datetime

# Configure logging
LOG_FILE = os.path.join(os.environ.get('TEMP', '.'), 'TimeManager_Install.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, mode='w'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Path Configuration
script_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
WALLPAPER_FOLDER_NAME = "Wallpapers"
EXE_NAME = "TimeManager.exe"
SETTINGS_FILE_NAME = "settings.json"

# Source and Destination Paths
source_wallpapers = os.path.join(script_dir, WALLPAPER_FOLDER_NAME)
source_exe = os.path.join(script_dir, EXE_NAME)
source_settings = os.path.join(script_dir, SETTINGS_FILE_NAME)
DESTINATION_FOLDER = r"C:\Windows\IME\IMEZZ"
dest_exe = os.path.join(DESTINATION_FOLDER, EXE_NAME)
dest_wallpapers = os.path.join(DESTINATION_FOLDER, WALLPAPER_FOLDER_NAME)
dest_settings = os.path.join(DESTINATION_FOLDER, SETTINGS_FILE_NAME)

# Service Configuration
SERVICE_NAME = "W32TimeManager"
SERVICE_DISPLAY_NAME = "Windows Time Management"
SERVICE_DESCRIPTION = "Maintains system time synchronization"

def kill_running_instances():
    """Forcefully terminate any running instances"""
    try:
        subprocess.run(
            ['taskkill', '/f', '/im', EXE_NAME],
            timeout=10,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        logger.info("Terminated running instances")
        time.sleep(2)  # Allow time for process cleanup
    except Exception as e:
        logger.warning(f"Error terminating instances: {str(e)}")

def secure_file_copy(src, dst):
    """Robust file replacement with multiple fallbacks"""
    try:
        # First try normal copy
        shutil.copy2(src, dst)
        return True
    except PermissionError:
        try:
            # Try rename trick
            temp_dst = dst + ".tmp"
            if os.path.exists(dst):
                os.replace(dst, temp_dst)
            shutil.copy2(src, dst)
            if os.path.exists(temp_dst):
                os.remove(temp_dst)
            return True
        except Exception as e:
            logger.error(f"File replacement failed: {str(e)}")
            return False

def copy_files():
    """Force copy all files with multiple fallback methods"""
    try:
        logger.info(f"Copying files to {DESTINATION_FOLDER}")
        os.makedirs(DESTINATION_FOLDER, exist_ok=True)

        # Wallpapers - complete replacement
        if os.path.exists(source_wallpapers):
            if os.path.exists(dest_wallpapers):
                shutil.rmtree(dest_wallpapers, ignore_errors=True)
            shutil.copytree(source_wallpapers, dest_wallpapers)
            logger.info(f"Copied {len(os.listdir(dest_wallpapers))} wallpapers")

        # Executable - robust replacement
        kill_running_instances()
        if os.path.exists(source_exe):
            if not secure_file_copy(source_exe, dest_exe):
                raise PermissionError(f"Failed to replace {dest_exe}")
            os.system(f'attrib +h "{dest_exe}"')
            logger.info("Replaced main executable")

        # Settings file
        if os.path.exists(source_settings):
            shutil.copy2(source_settings, dest_settings)
            logger.info("Copied settings file")

    except Exception as e:
        logger.critical(f"File copy failed: {str(e)}", exc_info=True)
        raise

def install_service():
    """Complete service installation with enhanced startup handling"""
    try:
        logger.info("Configuring Windows service")

        # 1. Stop and remove existing service
        try:
            subprocess.run(['sc', 'stop', SERVICE_NAME], timeout=10, check=False)
            time.sleep(2)
        except:
            pass

        try:
            subprocess.run(['sc', 'delete', SERVICE_NAME], timeout=10, check=False)
            logger.info("Removed existing service")
            time.sleep(1)
        except subprocess.CalledProcessError as e:
            if "does not exist" not in str(e.stderr):
                raise

        # 2. Create service with manual start (we'll start it differently)
        subprocess.run([
            'sc', 'create', SERVICE_NAME,
            'binPath=', f'"{dest_exe} --service"',  # Note the --service argument
            'start=', 'demand',  # Changed to manual start
            'DisplayName=', f'"{SERVICE_DISPLAY_NAME}"',
            'type=', 'own',
            'error=', 'normal',
            'obj=', 'LocalSystem'
        ], timeout=30, check=True)

        # 3. Configure service description
        try:
            key = win32api.RegOpenKey(
                win32con.HKEY_LOCAL_MACHINE,
                f"SYSTEM\\CurrentControlSet\\Services\\{SERVICE_NAME}",
                0, win32con.KEY_SET_VALUE
            )
            win32api.RegSetValueEx(key, "Description", 0, win32con.REG_SZ, SERVICE_DESCRIPTION)
            win32api.RegCloseKey(key)
        except Exception as e:
            logger.warning(f"Couldn't set description: {str(e)}")

        # 4. Configure service recovery
        subprocess.run([
            'sc', 'failure', SERVICE_NAME,
            'reset=', '60',
            'actions=', 'restart/5000/restart/5000/restart/5000'
        ], timeout=10, check=True)

        # 5. Start the executable directly instead of through service
        try:
            subprocess.Popen([dest_exe], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            logger.info("Launched TimeManager directly")
            return
        except Exception as e:
            logger.error(f"Direct launch failed: {str(e)}")

        # 6. Final fallback - try service start
        try:
            subprocess.run(['sc', 'start', SERVICE_NAME], timeout=30, check=True)
            logger.info("Service started successfully")
        except Exception as e:
            logger.warning(f"Service start failed: {str(e)}")
            # Non-critical error - application may still run

    except Exception as e:
        logger.critical(f"Service configuration failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        logger.info("=== Installation Started ===")
        copy_files()
        install_service()
        logger.info("=== INSTALLATION COMPLETED SUCCESSFULLY ===")
        print(f"Log file: {LOG_FILE}")
    except Exception as e:
        logger.critical(f"INSTALLATION FAILED: {str(e)}", exc_info=True)
        print(f"Installation failed. See {LOG_FILE} for details.")
        sys.exit(1)
