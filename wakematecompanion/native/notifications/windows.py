"""
Windows implementation of native notifications
"""

import os
import ctypes
from pathlib import Path
import logging
from .base import NotificationProvider

logger = logging.getLogger("WakeMATECompanion")

class WindowsNotificationProvider(NotificationProvider):
    """Windows implementation of native notifications using WinToast."""
    
    def __init__(self):
        # Load the native library
        self.lib_path = Path(__file__).parent.parent.parent / "bin" / "windows" / "wm_notifications.dll"
        
        if not self.lib_path.exists():
            logger.warning(f"Native library not found: {self.lib_path}")
            raise ImportError(f"Native library not found: {self.lib_path}")
        
        try:
            self.lib = ctypes.CDLL(str(self.lib_path))
            
            # Define function prototypes
            self.lib.show_notification.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
            self.lib.show_notification.restype = ctypes.c_bool
            
            logger.info("Windows notification provider initialized")
        except Exception as e:
            logger.error(f"Failed to load Windows notification library: {str(e)}")
            raise ImportError(f"Failed to load Windows notification library: {str(e)}")
    
    def show_notification(self, title: str, message: str, icon_path: str = None):
        """Show a Windows toast notification."""
        try:
            title_bytes = title.encode('utf-8')
            message_bytes = message.encode('utf-8')
            icon_bytes = icon_path.encode('utf-8') if icon_path else None
            
            success = self.lib.show_notification(title_bytes, message_bytes, icon_bytes)
            if not success:
                logger.warning("Failed to show Windows notification")
                return None
            
            logger.info("Windows notification shown successfully")
            # In this simple implementation, we don't track notification IDs
            return "windows-notification"
        except Exception as e:
            logger.error(f"Error showing Windows notification: {str(e)}")
            raise
    
    def remove_notification(self, notification_id: str):
        """Remove a notification - not supported on Windows."""
        # Windows doesn't provide a way to remove toast notifications programmatically
        logger.warning("Removing notifications is not supported on Windows")
        return False