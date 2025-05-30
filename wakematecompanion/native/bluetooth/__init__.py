"""
Native Bluetooth module interface for WakeMATECompanion
"""

import platform
import logging

from .base import BluetoothProvider
from .fallback import FallbackBluetoothProvider

# Import platform-specific implementations
logger = logging.getLogger("WakeMATECompanion")
system = platform.system()

# This module is for future implementation - currently using fallback for all platforms
logger.warning("Bluetooth module is a placeholder for future implementation")
PlatformBluetoothProvider = FallbackBluetoothProvider

# Create a singleton instance