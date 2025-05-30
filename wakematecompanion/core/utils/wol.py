"""
Wake-on-LAN functionality for WakeMATECompanion
"""

import socket
import re
import logging

logger = logging.getLogger("WakeMATECompanion")

def send_magic_packet(mac: str, broadcast: str = "255.255.255.255", port: int = 9):
    """Send a Wake-on-LAN magic packet
    
    Args:
        mac (str): MAC address in any common delimiter format
        broadcast (str, optional): Broadcast IP on the LAN. Defaults to "255.255.255.255".
        port (int, optional): UDP port (7 or 9 are standard). Defaults to 9.
    """
    try:
        # Normalize MAC address format
        mac_clean = re.sub(r'[^0-9a-fA-F]', '', mac)
        if len(mac_clean) != 12:
            raise ValueError("MAC address must be 12 hex digits")
        
        # Build magic packet: 6 bytes of 0xFF followed by the MAC address repeated 16 times
        magic_packet = bytes.fromhex('F' * 12)
        for _ in range(16):
            magic_packet += bytes.fromhex(mac_clean)
        
        # Send packet
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, (broadcast, port))
        
        logger.info(f"Sent WOL magic packet to {mac}")
    except Exception as e:
        logger.error(f"Failed to send WOL packet: {str(e)}")
        raise