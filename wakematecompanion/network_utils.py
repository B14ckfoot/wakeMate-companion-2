"""
Network utility functions for WakeMATECompanion
"""

import socket
import platform
import subprocess
import logging

logger = logging.getLogger("WakeMATECompanion")

def get_local_ip():
    """Get the local IP address of this machine"""
    try:
        # Create a socket that doesn't actually connect
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        logger.info(f"Local IP: {local_ip}")
        return local_ip
    except Exception as e:
        logger.warning(f"Failed to get local IP: {str(e)}")
        return "127.0.0.1"  # Fallback to localhost

def get_mac_from_ip(ip):
    """Get MAC address from IP address"""
    os_type = platform.system()
    try:
        logger.info(f"Getting MAC address for {ip}")
        
        if os_type == "Windows":
            # Use ARP to get MAC
            output = subprocess.check_output(f"arp -a {ip}", shell=True).decode('utf-8')
            for line in output.splitlines():
                if ip in line:
                    mac = line.split()[1].replace("-", ":")
                    logger.info(f"MAC for {ip}: {mac}")
                    return mac
        
        elif os_type == "Darwin":  # macOS
            output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
            for line in output.splitlines():
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[3]
                        logger.info(f"MAC for {ip}: {mac}")
                        return mac
        
        elif os_type == "Linux":
            output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
            for line in output.splitlines():
                if ip in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                        logger.info(f"MAC for {ip}: {mac}")
                        return mac
        
        logger.warning(f"Could not determine MAC for {ip}")
        return None
    
    except Exception as e:
        logger.error(f"Failed to get MAC: {str(e)}")
        return None

def get_local_mac():
    """Get the MAC address of the current machine"""
    local_ip = get_local_ip()
    return get_mac_from_ip(local_ip)