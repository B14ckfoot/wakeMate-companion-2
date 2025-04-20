"""
Logging configuration module for WakeMATECompanion
"""

import os
import logging
from datetime import datetime

def setup_logging():
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(app_path, "wakeMate.log")
    
    # Configure logging
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("WakeMATECompanion")
    logger.info("WakeMATECompanion initializing...")
    
    return logger