"""
System control utilities for WakeMATECompanion
"""

import platform
import subprocess
import logging

logger = logging.getLogger("WakeMATECompanion")

def shutdown():
    """Shutdown the system"""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'], check=True)
        elif system == "Linux":
            subprocess.run(["shutdown", "-h", "now"], check=True)
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        logger.info("Shutdown command executed")
    except Exception as e:
        logger.error(f"Failed to execute shutdown: {str(e)}")
        raise

def restart():
    """Restart the system"""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell app "System Events" to restart'], check=True)
        elif system == "Linux":
            subprocess.run(["shutdown", "-r", "now"], check=True)
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        logger.info("Restart command executed")
    except Exception as e:
        logger.error(f"Failed to execute restart: {str(e)}")
        raise

def sleep():
    """Put the system to sleep"""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["powercfg", "-hibernate", "off"], check=True)
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell app "System Events" to sleep'], check=True)
        elif system == "Linux":
            subprocess.run(["systemctl", "suspend"], check=True)
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        logger.info("Sleep command executed")
    except Exception as e:
        logger.error(f"Failed to execute sleep: {str(e)}")
        raise

def logoff():
    """Log off the current user"""
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.run(["shutdown", "/l"], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["osascript", "-e", 'tell app "System Events" to log out'], check=True)
        elif system == "Linux":
            subprocess.run(["gnome-session-quit", "--logout", "--no-prompt"], check=True)
        else:
            raise ValueError(f"Unsupported platform: {system}")
        
        logger.info("Logoff command executed")
    except Exception as e:
        logger.error(f"Failed to execute logoff: {str(e)}")
        raise