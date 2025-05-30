"""
Native notification system for WakeMATECompanion
"""

import platform
import logging

from .base import NotificationProvider
from .fallback import FallbackNotificationProvider

# Import platform-specific implementations
logger = logging.getLogger("WakeMATECompanion")
system = platform.system()

if system == 'Windows':
    try:
        from .windows import WindowsNotificationProvider as PlatformNotificationProvider
        logger.info("Using Windows notification provider")
    except ImportError as e:
        logger.warning(f"Windows notification provider not available: {str(e)}")
        logger.warning("Falling back to basic implementation")
        PlatformNotificationProvider = FallbackNotificationProvider
elif system == 'Darwin':  # macOS
    try:
        from .macos import MacOSNotificationProvider as PlatformNotificationProvider
        logger.info("Using macOS notification provider")
    except ImportError as e:
        logger.warning(f"macOS notification provider not available: {str(e)}")
        logger.warning("Falling back to basic implementation")
        PlatformNotificationProvider = FallbackNotificationProvider
else:
    logger.warning(f"Unsupported platform: {system}, using fallback notification provider")
    PlatformNotificationProvider = FallbackNotificationProvider

# Create a singleton instance
provider = PlatformNotificationProvider()

# Export function wrappers
def show_notification(title: str, message: str, icon_path: str = None):
    """Show a notification with the given title and message"""
    return provider.show_notification(title, message, icon_path)

def remove_notification(notification_id: str):
    """Remove a notification by its ID"""
    return provider.remove_notification(notification_id)