"""
macOS implementation of native notifications
"""

import os
from pathlib import Path
import ctypes
import logging
import subprocess
import platform
from .base import NotificationProvider

logger = logging.getLogger("WakeMATECompanion")

class MacOSNotificationProvider(NotificationProvider):
    """macOS implementation of native notifications."""
    
    def __init__(self):
        # Check for native library
        self.lib_path = Path(__file__).parent.parent.parent / "bin" / "macos" / "libwm_notifications.dylib"
        
        # First attempt: use native library if available
        if self.lib_path.exists():
            try:
                self.lib = ctypes.CDLL(str(self.lib_path))
                
                # Define function prototypes
                self.lib.show_notification.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
                self.lib.show_notification.restype = ctypes.c_bool
                
                self.use_native = True
                logger.info("macOS native notification provider initialized")
            except Exception as e:
                logger.error(f"Failed to load macOS notification library: {str(e)}")
                self.use_native = False
        else:
            # Second attempt: use AppleScript as a fallback
            logger.warning(f"Native library not found: {self.lib_path}")
            logger.info("Using AppleScript for notifications instead")
            self.use_native = False
    
    def show_notification(self, title: str, message: str, icon_path: str = None):
        """Show a macOS notification."""
        if self.use_native:
            try:
                title_bytes = title.encode('utf-8')
                message_bytes = message.encode('utf-8')
                icon_bytes = icon_path.encode('utf-8') if icon_path else None
                
                success = self.lib.show_notification(title_bytes, message_bytes, icon_bytes)
                if not success:
                    logger.warning("Failed to show macOS notification using native library")
                    # Fall back to AppleScript
                    return self._show_notification_applescript(title, message)
                
                logger.info("macOS notification shown successfully using native library")
                return "macos-notification-native"
            except Exception as e:
                logger.error(f"Error showing macOS notification using native library: {str(e)}")
                # Fall back to AppleScript
                return self._show_notification_applescript(title, message)
        else:
            return self._show_notification_applescript(title, message)
    
    def _show_notification_applescript(self, title: str, message: str):
        """Show a notification using AppleScript."""
        try:
            # Escape double quotes in the strings
            title_escaped = title.replace('"', '\\"')
            message_escaped = message.replace('"', '\\"')
            
            # Create the AppleScript command
            script = f'''
            display notification "{message_escaped}" with title "{title_escaped}"
            '''
            
            # Execute the AppleScript
            subprocess.run(['osascript', '-e', script], check=True)
            
            logger.info("macOS notification shown successfully using AppleScript")
            return "macos-notification-applescript"
        except Exception as e:
            logger.error(f"Error showing macOS notification using AppleScript: {str(e)}")
            raise
    
    def remove_notification(self, notification_id: str):
        """Remove a notification - limited support on macOS."""
        # Not directly supported in a simple way
        logger.warning("Removing notifications is not supported on macOS")
        return False