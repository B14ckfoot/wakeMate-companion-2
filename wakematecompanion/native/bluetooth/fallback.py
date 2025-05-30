"""
Fallback Bluetooth provider for when native modules are not available
"""

import logging
from typing import List, Dict, Any, Optional
from .base import BluetoothProvider

logger = logging.getLogger("WakeMATECompanion")

class FallbackBluetoothProvider(BluetoothProvider):
    """Fallback Bluetooth provider that logs operations but does not perform them."""
    
    def __init__(self):
        logger.warning("Using fallback Bluetooth provider - no actual Bluetooth functionality available")
    
    def start_discovery(self):
        """Start discovering Bluetooth devices."""
        logger.warning("Bluetooth discovery not available in fallback mode")
    
    def stop_discovery(self):
        """Stop discovering Bluetooth devices."""
        logger.warning("Bluetooth discovery not available in fallback mode")
    
    def get_paired_devices(self) -> List[Dict[str, Any]]:
        """Get a list of paired Bluetooth devices."""
        logger.warning("Cannot get paired Bluetooth devices in fallback mode")
        return []
    
    def connect(self, device_id: str) -> bool:
        """Connect to a Bluetooth device."""
        logger.warning(f"Cannot connect to Bluetooth device {device_id} in fallback mode")
        return False
    
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from a Bluetooth device."""
        logger.warning(f"Cannot disconnect from Bluetooth device {device_id} in fallback mode")
        return False
    
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a Bluetooth device."""
        logger.warning(f"Cannot send data to Bluetooth device {device_id} in fallback mode")
        return False