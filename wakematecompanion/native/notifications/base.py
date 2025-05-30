"""
Base class for native notifications
"""

from abc import ABC, abstractmethod

class NotificationProvider(ABC):
    """Abstract base class for native notifications."""
    
    @abstractmethod
    def show_notification(self, title: str, message: str, icon_path: str = None):
        """Show a notification with the given title and message.
        
        Args:
            title (str): The notification title
            message (str): The notification message
            icon_path (str, optional): Path to an icon to display. Defaults to None.
            
        Returns:
            str: A notification ID or None
        """
        pass
    
    @abstractmethod
    def remove_notification(self, notification_id: str):
        """Remove a notification by its ID.
        
        Args:
            notification_id (str): The notification ID to remove
            
        Returns:
            bool: True if the notification was removed, False otherwise
        """
        pass