"""
QR code generation functionality for WakeMATECompanion
"""

import os
import json
import platform
import subprocess
import logging

logger = logging.getLogger("WakeMATECompanion")

# Optional imports - will be handled gracefully if not available
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("QR code module not available. Install with: pip install qrcode")

def is_available():
    """Check if QR code generation is available"""
    return QRCODE_AVAILABLE

def generate_qr_code(server_ip, server_port, local_mac=None):
    """Generate a QR code with the connection information
    
    Args:
        server_ip (str): The server IP address
        server_port (int): The server port
        local_mac (str, optional): The local MAC address
        
    Returns:
        str: Path to the generated QR code or None if failed
    """
    if not QRCODE_AVAILABLE:
        logger.error("QR code module not available")
        return None
            
    try:
        logger.info("Generating QR code")
        
        # Create connection info for QR code
        connection_info = {
            "app": "WakeMATECompanion",
            "serverIP": server_ip,
            "serverPort": server_port,
            "localMAC": local_mac
        }
        
        # Convert to JSON string
        data = json.dumps(connection_info)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create an image from the QR Code
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save the image
        app_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        qr_path = os.path.join(app_path, "wakemateqr.png")
        img.save(qr_path)
        
        # Open the image with default viewer
        os_type = platform.system()
        if os_type == "Windows":
            os.startfile(qr_path)
        elif os_type == "Darwin":  # macOS
            subprocess.call(["open", qr_path])
        elif os_type == "Linux":
            subprocess.call(["xdg-open", qr_path])
        
        logger.info(f"QR code saved to {qr_path}")
        return qr_path
    
    except Exception as e:
        logger.error(f"Failed to generate QR code: {str(e)}")
        return None