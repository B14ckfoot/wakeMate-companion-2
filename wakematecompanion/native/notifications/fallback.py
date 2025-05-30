"""
Fallback notification provider using Python-only methods
"""

import platform
import logging
import subprocess
import os
from .base import NotificationProvider

logger = logging.getLogger("WakeMATECompanion")

class FallbackNotificationProvider(NotificationProvider):
    """Fallback notification provider using Python-only methods."""
    
    def __init__(self):
        self.system = platform.system()
        
        # Try to use platform-agnostic notification libraries
        try:
            import plyer
            self.use_plyer = True
            logger.info("Using Plyer for fallback notifications")
        except ImportError:
            self.use_plyer = False
            logger.warning("Plyer not available, using system-specific fallbacks for notifications")
    
    def show_notification(self, title: str, message: str, icon_path: str = None):
        """Show a notification using available Python libraries."""
        if self.use_plyer:
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    app_name="WakeMATECompanion",
                    app_icon=icon_path
                )
                logger.info("Notification shown successfully using Plyer")
                return "plyer-notification"
            except Exception as e:
                logger.error(f"Plyer notification failed: {str(e)}")
        
        # System-specific fallbacks
        if self.system == "Windows":
            return self._show_windows_fallback(title, message)
        elif self.system == "Darwin":  # macOS
            return self._show_macos_fallback(title, message)
        elif self.system == "Linux":
            return self._show_linux_fallback(title, message)
        
        # Ultimate fallback is just logging
        logger.info(f"Notification (logged): {title} - {message}")
        return None
    
    def _show_windows_fallback(self, title, message):
        """Windows-specific fallback for notifications."""
        try:
            # Try to use PowerShell for notifications
            # Escape single quotes in the strings
            title_escaped = title.replace("'", "''")
            message_escaped = message.replace("'", "''")
            
            powershell_cmd = f'''
            powershell -Command "& {{
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null;
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime] | Out-Null;
                
                $template = [Windows.UI.Notifications.ToastTemplateType]::ToastText02;
                $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent($template);
                
                $text = $xml.GetElementsByTagName('text');
                $text[0].AppendChild($xml.CreateTextNode('{title_escaped}'));
                $text[1].AppendChild($xml.CreateTextNode('{message_escaped}'));
                
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml);
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('WakeMATECompanion').Show($toast);
            }}"
            '''
            
            subprocess.run(powershell_cmd, shell=True, check=True)
            logger.info("Notification shown successfully using PowerShell")
            return "windows-powershell-notification"
        except Exception as e:
            logger.error(f"PowerShell notification failed: {str(e)}")
            # Just log the notification
            logger.info(f"Notification (logged): {title} - {message}")
            return None
    
    def _show_macos_fallback(self, title, message):
        """macOS-specific fallback for notifications."""
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
            
            logger.info("Notification shown successfully using AppleScript")
            return "macos-applescript-notification"
        except Exception as e:
            logger.error(f"AppleScript notification failed: {str(e)}")
            # Just log the notification
            logger.info(f"Notification (logged): {title} - {message}")
            return None
    
    def _show_linux_fallback(self, title, message):
        """Linux-specific fallback for notifications."""
        try:
            # Try to use notify-send
            subprocess.run(['notify-send', title, message], check=True)
            logger.info("Notification shown successfully using notify-send")
            return "linux-notify-send-notification"
        except Exception as e:
            logger.error(f"notify-send notification failed: {str(e)}")
            # Just log the notification
            logger.info(f"Notification (logged): {title} - {message}")
            return None
    
    def remove_notification(self, notification_id: str):
        """Remove a notification - not supported in fallback mode."""
        logger.warning("Removing notifications is not supported in fallback mode")
        return False