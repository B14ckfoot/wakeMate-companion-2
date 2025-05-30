"""
System tray implementation for WakeMATECompanion
"""

import os
import platform
import logging
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

from . import qr_generator
from .utils import network_utils
from ..native.notifications import show_notification

logger = logging.getLogger("WakeMATECompanion")

class WakeMateTray:
    """System tray interface for WakeMATECompanion"""
    
    def __init__(self, server):
        """Initialize the system tray
        
        Args:
            server: The server instance
        """
        self.server = server
        self.icon = None
        
        # Application paths
        self.app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.icon_path = os.path.join(self.app_path, "resources", "icon.png")
        
        # Create resources directory if it doesn't exist
        os.makedirs(os.path.join(self.app_path, "resources", "icons"), exist_ok=True)
        
        # Create default icon if it doesn't exist
        self.create_default_icon()
        
        # Set up server notification callback
        self.server.set_notification_callback(self.show_notification)
    
    def create_default_icon(self):
        """Create a default icon if one doesn't exist"""
        if not os.path.exists(self.icon_path):
            try:
                # Create a simple icon - a blue circle
                img = Image.new('RGB', (64, 64), color=(255, 255, 255))
                d = ImageDraw.Draw(img)
                d.ellipse((5, 5, 59, 59), fill=(0, 120, 212))
                img.save(self.icon_path)
                logger.info(f"Created default icon at {self.icon_path}")
            except Exception as e:
                logger.error(f"Failed to create default icon: {str(e)}")
    
    def create_system_tray(self):
        """Create the system tray icon and menu"""
        try:
            icon_image = Image.open(self.icon_path)
            
            # Define dynamic menu text for server status
            def server_status(item):
                return f"Server: {'Online' if self.server.running else 'Offline'}"
            
            # Create menu
            menu = (
                item(server_status, lambda: None, enabled=False),
                item('Toggle Server', self.toggle_server),
                item('Generate QR Code', self.generate_qr_code, enabled=qr_generator.is_available()),
                item('Exit', self.exit_app)
            )
            
            # Create icon with title showing server status
            server_ip = self.server.ip
            title = f"WakeMATECompanion ({server_ip})"
            self.icon = pystray.Icon("WakeMATECompanion", icon_image, title, menu)
            return self.icon
        except Exception as e:
            logger.error(f"Failed to create system tray: {str(e)}")
            return None
    
    def update_tray_title(self):
        """Update the system tray icon title"""
        if self.icon:
            status = 'Online' if self.server.running else 'Offline'
            self.icon.title = f"WakeMATECompanion - {status} ({self.server.ip})"
    
    def toggle_server(self):
        """Toggle the server on/off"""
        if self.server.running:
            self.server.stop()
        else:
            self.server.start()
        
        self.update_tray_title()
    
    def generate_qr_code(self):
        """Generate a QR code with connection information"""
        if not self.server.running:
            self.show_notification("Server Not Running", "Start the server first")
            return
        
        # Get local MAC address
        local_mac = network_utils.get_local_mac()
        
        # Generate QR code
        qr_path = qr_generator.generate_qr_code(
            self.server.ip, 
            self.server.port,
            local_mac
        )
        
        if qr_path:
            self.show_notification(
                "QR Code Generated", 
                f"QR code saved to {qr_path}"
            )
    
    def show_notification(self, title, message):
        """Show a system notification"""
        logger.info(f"Notification: {title} - {message}")
        
        try:
            # Use our new native notification system
            show_notification(title, message, self.icon_path)
        except Exception as e:
            logger.error(f"Failed to show notification: {str(e)}")
            
            # Fallback to pystray notification if available
            if self.icon:
                try:
                    self.icon.notify(message, title)
                except Exception as e2:
                    logger.error(f"Failed to show pystray notification: {str(e2)}")
    
    def run(self):
        """Run the system tray"""
        try:
            # Create and run system tray icon
            icon = self.create_system_tray()
            if icon:
                logger.info("Starting system tray icon")
                icon.run()
                return True
            else:
                logger.error("Failed to create system tray icon")
                return False
        except Exception as e:
            logger.error(f"Failed to run system tray: {str(e)}")
            return False
    
    def exit_app(self):
        """Exit the application"""
        logger.info("Exiting application")
        
        # Stop server if running
        if self.server.running:
            self.server.stop()
        
        # Stop icon
        if self.icon:
            self.icon.stop()
        
        logger.info("Application exited")