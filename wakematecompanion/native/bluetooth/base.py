"""
Base class for native Bluetooth functionality
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BluetoothProvider(ABC):
    """Abstract base class for native Bluetooth functionality."""
    
    @abstractmethod
    def start_discovery(self):
        """Start discovering Bluetooth devices."""
        pass
    
    @abstractmethod
    def stop_discovery(self):
        """Stop discovering Bluetooth devices."""
        pass
    
    @abstractmethod
    def get_paired_devices(self) -> List[Dict[str, Any]]:
        """Get a list of paired Bluetooth devices.
        
        Returns:
            List[Dict[str, Any]]: A list of paired devices, each represented as a dictionary
        """
        pass
    
    @abstractmethod
    def connect(self, device_id: str) -> bool:
        """Connect to a Bluetooth device.
        
        Args:
            device_id (str): The ID of the device to connect to
            
        Returns:
            bool: True if the connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self, device_id: str) -> bool:
        """Disconnect from a Bluetooth device.
        
        Args:
            device_id (str): The ID of the device to disconnect from
            
        Returns:
            bool: True if the disconnection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def send_data(self, device_id: str, data: bytes) -> bool:
        """Send data to a Bluetooth device.
        
        Args:
            device_id (str): The ID of the device to send data to
            data (bytes): The data to send
            
        Returns:
            bool: True if the data was sent successfully, False otherwise
        """
        pass