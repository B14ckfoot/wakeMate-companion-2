"""
Main entry point for WakeMATECompanion
"""

import sys
import os
import logging

from . import logging_config
from . import network_utils
from .server import WakeMateServer
from .system_tray import WakeMateTray

def main():
    """Main entry point for the application"""
    try:
        # Setup logging
        logger = logging_config.setup_logging()
        
        # Get local IP
        server_ip = network_utils.get_local_ip()
        
        # Create server
        server = WakeMateServer(server_ip)
        
        # Start server automatically
        server.start()
        
        # Create and run system tray
        tray = WakeMateTray(server)
        tray.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()