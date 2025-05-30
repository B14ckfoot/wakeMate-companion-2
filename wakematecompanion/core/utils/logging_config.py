"""
Logging configuration module for WakeMATECompanion
"""

import os
import logging
from datetime import datetime
from pathlib import Path

def setup_logging():
    """Configure application logging"""
    # Create logs directory if it doesn't exist
    app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(app_path, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = os.path.join(log_dir, f"wakemate-{timestamp}.log")
    
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