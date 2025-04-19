import sys
import socket
import platform
import threading
import subprocess
import time
import json
import os
import logging
from datetime import datetime
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import pyautogui

# Optional imports - will be handled gracefully if not available
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

class WakeMATECompanion:
    """
    WakeMATECompanion - A cross-platform utility for remote system control
    Allows mobile devices to send wake/sleep/media control commands to this computer
    """
    
    def __init__(self):
        # Setup logging
        self.setup_logging()
        
        # System information
        self.os_type = platform.system()
        self.connected = False
        self.target_ip = None
        self.target_mac = None
        
        # Application paths
        self.app_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(self.app_path, "icon.png")
        self.log_path = os.path.join(self.app_path, "wakeMate.log")
        self.create_default_icon()
        
        # Server configuration
        self.server_ip = self.get_local_ip()
        self.server_port = 7777
        self.server_running = False
        self.server_socket = None
        self.connected_clients = []
        
        # Auto-start monitor
        self.auto_start_thread = None
        self.auto_start_running = False
        
        # System tray icon
        self.icon = None
    
    def setup_logging(self):
        """Configure logging for the application"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "wakeMate.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("WakeMATECompanion")
        self.logger.info("WakeMATECompanion initializing...")
    
    def create_default_icon(self):
        """Create a default icon if one doesn't exist"""
        if not os.path.exists(self.icon_path):
            try:
                # Create a simple icon - a blue circle
                img = Image.new('RGB', (64, 64), color=(255, 255, 255))
                d = ImageDraw.Draw(img)
                d.ellipse((5, 5, 59, 59), fill=(0, 120, 212))
                img.save(self.icon_path)
                self.logger.info(f"Created default icon at {self.icon_path}")
            except Exception as e:
                self.logger.error(f"Failed to create default icon: {str(e)}")
    
    def get_local_ip(self):
        """Get the local IP address of this machine"""
        try:
            # Create a socket that doesn't actually connect
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            self.logger.info(f"Local IP: {local_ip}")
            return local_ip
        except Exception as e:
            self.logger.warning(f"Failed to get local IP: {str(e)}")
            return "127.0.0.1"  # Fallback to localhost
    
    def create_system_tray(self):
        """Create the system tray icon and menu"""
        try:
            icon_image = Image.open(self.icon_path)
            
            # Define dynamic menu text for server status
            def server_status(item):
                return f"Server: {'Online' if self.server_running else 'Offline'}"
            
            def auto_status(item):
                return f"Auto-Start: {'Enabled' if self.auto_start_running else 'Disabled'}"
            
            # Create menu with better organization
            menu = (
                item(server_status, lambda: None, enabled=False),
                item(auto_status, lambda: None, enabled=False),
                item('Server Controls', (
                    item('Start Server', self.start_server),
                    item('Stop Server', self.stop_server),
                    item('Show Connection Info', self.show_connection_info)
                )),
                item('Auto-Start', (
                    item('Enable Auto-Start', self.enable_auto_start),
                    item('Disable Auto-Start', self.disable_auto_start),
                )),
                item('Tools', (
                    item('Generate QR Code', self.generate_qr_code, enabled=QRCODE_AVAILABLE),
                    item('Scan Network', self.scan_network),
                    item('View Logs', self.view_logs)
                )),
                item('Exit', self.exit_app)
            )
            
            # Create icon with title showing server status
            title = f"WakeMATECompanion ({self.server_ip})"
            self.icon = pystray.Icon("WakeMATECompanion", icon_image, title, menu)
            return self.icon
        except Exception as e:
            self.logger.error(f"Failed to create system tray: {str(e)}")
            return None
    
    def update_tray_title(self):
        """Update the system tray icon title"""
        if self.icon:
            status = 'Online' if self.server_running else 'Offline'
            auto = 'Auto-On' if self.auto_start_running else ''
            self.icon.title = f"WakeMATECompanion - {status} {auto} ({self.server_ip})"
    
    def run(self):
        """Run the application"""
        try:
            # Start server automatically
            self.start_server()
            
            # Start auto-start monitor
            self.enable_auto_start()
            
            # Create and run system tray icon
            icon = self.create_system_tray()
            if icon:
                self.logger.info("Starting system tray icon")
                icon.run()
            else:
                self.logger.error("Failed to create system tray icon, exiting")
                sys.exit(1)
        except Exception as e:
            self.logger.error(f"Failed to run application: {str(e)}")
            sys.exit(1)
    
    def show_notification(self, title, message):
        """Show a system notification"""
        self.logger.info(f"Notification: {title} - {message}")
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                self.logger.error(f"Failed to show notification: {str(e)}")
    
    def view_logs(self):
        """Open the log file with the default application"""
        try:
            if self.os_type == "Windows":
                os.startfile(self.log_path)
            elif self.os_type == "Darwin":  # macOS
                subprocess.call(["open", self.log_path])
            elif self.os_type == "Linux":
                subprocess.call(["xdg-open", self.log_path])
            else:
                self.show_notification("Error", f"Unsupported OS: {self.os_type}")
        except Exception as e:
            self.show_notification("Error", f"Failed to open log file: {str(e)}")
    
    #
    # Server functions
    #
    
    def start_server(self):
        """Start the server for phone app communication"""
        if self.server_running:
            self.logger.info("Server is already running")
            return
        
        try:
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.server_running = True
            self.update_tray_title()
            self.logger.info(f"Server started on {self.server_ip}:{self.server_port}")
            self.show_notification("Server Started", f"Listening on {self.server_ip}:{self.server_port}")
        except Exception as e:
            self.logger.error(f"Failed to start server: {str(e)}")
            self.show_notification("Error", f"Failed to start server: {str(e)}")
    
    def _run_server(self):
        """Server thread function"""
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(5)
            self.server_socket.settimeout(1.0)  # Add timeout for accepting connections
            
            self.logger.info(f"Server listening on {self.server_ip}:{self.server_port}")
            
            while self.server_running:
                try:
                    # Accept connection
                    client_sock, addr = self.server_socket.accept()
                    
                    # Handle client in a new thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_sock, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # Add to clients list
                    self.connected_clients.append((client_sock, addr))
                    
                    # Log connection
                    self.logger.info(f"New connection from {addr[0]}")
                    self.show_notification("New Connection", f"Device at {addr[0]} connected")
                
                except socket.timeout:
                    continue  # Timeout allows checking server_running flag
                except Exception as e:
                    if self.server_running:  # Only show errors if server should be running
                        self.logger.error(f"Server error: {str(e)}")
                    break
        
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
        
        finally:
            # Clean up if thread exits
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            self.logger.info("Server stopped")
    
    def _handle_client(self, client_sock, addr):
        """Handle communication with a connected client"""
        client_addr = f"{addr[0]}:{addr[1]}"
        self.logger.info(f"Handling client connection from {client_addr}")
        
        try:
            # Set a timeout to allow checking server_running flag
            client_sock.settimeout(1.0)
            
            while self.server_running:
                try:
                    # Receive data
                    data = client_sock.recv(1024)
                    
                    if not data:
                        # Client disconnected
                        self.logger.info(f"Client {client_addr} disconnected")
                        break
                    
                    # Process command
                    self._process_command(data.decode('utf-8'), client_sock, client_addr)
                
                except socket.timeout:
                    continue
                except json.JSONDecodeError as e:
                    self.logger.warning(f"Invalid JSON from {client_addr}: {str(e)}")
                    response = {"status": "error", "message": "Invalid JSON format"}
                    client_sock.sendall(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    self.logger.error(f"Error handling client {client_addr}: {str(e)}")
                    break
        
        finally:
            # Remove client from list and close socket
            if (client_sock, addr) in self.connected_clients:
                self.connected_clients.remove((client_sock, addr))
            
            client_sock.close()
            self.logger.info(f"Connection closed with {client_addr}")
    
    def _process_command(self, command_str, client_sock, client_addr):
        """Process a command from the client"""
        try:
            # Parse JSON command
            command = json.loads(command_str)
            
            # Extract command type and parameters
            cmd_type = command.get("command", "")
            params = command.get("params", {})
            
            self.logger.info(f"Received command '{cmd_type}' from {client_addr}")
            
            # Execute command and build response
            result = {"status": "success", "message": "Command executed"}
            
            if cmd_type == "wake":
                self.wake_computer()
            
            elif cmd_type == "sleep":
                self.sleep_computer()
            
            elif cmd_type == "restart":
                self.restart_computer()
            
            elif cmd_type == "shutdown":
                self.shutdown_computer()
            
            elif cmd_type == "media_play_pause":
                self.media_play_pause()
            
            elif cmd_type == "media_next":
                self.media_next()
            
            elif cmd_type == "media_prev":
                self.media_previous()
            
            elif cmd_type == "volume_up":
                self.volume_up()
            
            elif cmd_type == "volume_down":
                self.volume_down()
            
            elif cmd_type == "volume_mute":
                self.volume_mute()
            
            elif cmd_type == "mouse_move":
                # Move mouse to specified position
                x = params.get("x", 0)
                y = params.get("y", 0)
                pyautogui.moveTo(x, y)
            
            elif cmd_type == "mouse_click":
                # Perform mouse click
                button = params.get("button", "left")
                pyautogui.click(button=button)
            
            elif cmd_type == "key_press":
                # Press a keyboard key
                key = params.get("key", "")
                if key:
                    pyautogui.press(key)
            
            elif cmd_type == "text_input":
                # Type text
                text = params.get("text", "")
                if text:
                    pyautogui.write(text)
            
            elif cmd_type == "get_status":
                # Return status information
                result = {
                    "status": "success",
                    "data": {
                        "os": self.os_type,
                        "server_ip": self.server_ip,
                        "server_port": self.server_port,
                        "target_ip": self.target_ip,
                        "target_mac": self.target_mac,
                        "connected": self.connected,
                        "auto_start": self.auto_start_running
                    }
                }
            
            else:
                # Unknown command
                self.logger.warning(f"Unknown command '{cmd_type}' from {client_addr}")
                result = {"status": "error", "message": f"Unknown command: {cmd_type}"}
            
            # Send response
            response = json.dumps(result)
            client_sock.sendall(response.encode('utf-8'))
            
        except json.JSONDecodeError:
            # Invalid JSON
            self.logger.warning(f"Invalid JSON from {client_addr}")
            response = json.dumps({"status": "error", "message": "Invalid JSON command"})
            client_sock.sendall(response.encode('utf-8'))
        
        except Exception as e:
            # Other errors
            self.logger.error(f"Error processing command from {client_addr}: {str(e)}")
            response = json.dumps({"status": "error", "message": str(e)})
            client_sock.sendall(response.encode('utf-8'))
    
    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            self.logger.info("Server is not running")
            return
        
        try:
            # Stop server
            self.server_running = False
            
            # Close all client connections
            for client_sock, addr in self.connected_clients:
                try:
                    client_sock.close()
                    self.logger.info(f"Closed connection to {addr[0]}:{addr[1]}")
                except:
                    pass
            
            self.connected_clients = []
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            self.update_tray_title()
            self.logger.info("Server stopped")
            self.show_notification("Server Stopped", "Server has been stopped")
        
        except Exception as e:
            self.logger.error(f"Failed to stop server: {str(e)}")
            self.show_notification("Error", f"Failed to stop server: {str(e)}")
    
    def show_connection_info(self):
        """Show connection information for phone app"""
        if not self.server_running:
            self.show_notification("Server Not Running", "Start the server first")
            return
        
        info = f"Server IP: {self.server_ip}\n"
        info += f"Server Port: {self.server_port}\n\n"
        
        if QRCODE_AVAILABLE:
            info += "Use 'Generate QR Code' to connect quickly\n"
            info += "or manually enter the connection details."
        else:
            info += "Enter these details in your WakeMate mobile app."
        
        self.show_notification("Connection Info", info)
    
    #
    # Auto-start monitoring functions
    #
    
    def enable_auto_start(self):
        """Enable the auto-start monitor"""
        if self.auto_start_running:
            self.logger.info("Auto-start is already enabled")
            return
        
        try:
            # Start auto-start monitor in a separate thread
            self.auto_start_thread = threading.Thread(target=self._run_auto_start_monitor)
            self.auto_start_thread.daemon = True
            self.auto_start_thread.start()
            
            self.auto_start_running = True
            self.update_tray_title()
            self.logger.info("Auto-start monitor enabled")
            self.show_notification("Auto-Start Enabled", "Will automatically start server when system wakes up")
        
        except Exception as e:
            self.logger.error(f"Failed to enable auto-start: {str(e)}")
            self.show_notification("Error", f"Failed to enable auto-start: {str(e)}")
    
    def _run_auto_start_monitor(self):
        """Auto-start monitor thread function"""
        self.logger.info("Auto-start monitor started")
        
        last_check_time = datetime.now()
        
        while self.auto_start_running:
            try:
                # Sleep for a bit to prevent CPU usage
                time.sleep(5)
                
                current_time = datetime.now()
                time_diff = (current_time - last_check_time).total_seconds()
                
                # If more than 30 seconds have passed, system might have been sleeping
                if time_diff > 30:
                    self.logger.info(f"System resumed after {time_diff} seconds")
                    
                    # Start server if it's not running
                    if not self.server_running:
                        self.logger.info("Auto-starting server after system wake")
                        # Use a separate thread to start the server to avoid blocking
                        threading.Thread(target=self.start_server).start()
                
                last_check_time = current_time
            
            except Exception as e:
                self.logger.error(f"Error in auto-start monitor: {str(e)}")
                time.sleep(10)  # Wait longer if there's an error
    
    def disable_auto_start(self):
        """Disable the auto-start monitor"""
        if not self.auto_start_running:
            self.logger.info("Auto-start is not enabled")
            return
        
        try:
            self.auto_start_running = False
            self.update_tray_title()
            self.logger.info("Auto-start monitor disabled")
            self.show_notification("Auto-Start Disabled", "Server will not automatically start on wake")
        
        except Exception as e:
            self.logger.error(f"Failed to disable auto-start: {str(e)}")
            self.show_notification("Error", f"Failed to disable auto-start: {str(e)}")
    
    #
    # Media control functions
    #
    
    def media_play_pause(self):
        """Send media play/pause command"""
        try:
            pyautogui.press('playpause')
            self.logger.info("Media play/pause command sent")
        except Exception as e:
            self.logger.error(f"Failed to send media play/pause: {str(e)}")
    
    def media_next(self):
        """Send media next track command"""
        try:
            pyautogui.press('nexttrack')
            self.logger.info("Media next track command sent")
        except Exception as e:
            self.logger.error(f"Failed to send media next track: {str(e)}")
    
    def media_previous(self):
        """Send media previous track command"""
        try:
            pyautogui.press('prevtrack')
            self.logger.info("Media previous track command sent")
        except Exception as e:
            self.logger.error(f"Failed to send media previous track: {str(e)}")
    
    def volume_up(self):
        """Increase volume"""
        try:
            pyautogui.press('volumeup')
            self.logger.info("Volume up command sent")
        except Exception as e:
            self.logger.error(f"Failed to send volume up: {str(e)}")
    
    def volume_down(self):
        """Decrease volume"""
        try:
            pyautogui.press('volumedown')
            self.logger.info("Volume down command sent")
        except Exception as e:
            self.logger.error(f"Failed to send volume down: {str(e)}")
    
    def volume_mute(self):
        """Mute/unmute volume"""
        try:
            pyautogui.press('volumemute')
            self.logger.info("Volume mute command sent")
        except Exception as e:
            self.logger.error(f"Failed to send volume mute: {str(e)}")
    
    #
    # System control functions
    #
    
    def wake_computer(self):
        """Wake the target computer using Wake-on-LAN"""
        if not self.target_mac:
            self.logger.warning("No MAC address set for wake command")
            self.show_notification("Error", "No MAC address set")
            return
        
        try:
            # Convert MAC address format from XX:XX:XX:XX:XX:XX to XXXXXXXXXXXX
            mac = self.target_mac.replace(":", "").replace("-", "")
            
            # Create magic packet
            magic_packet = b'\xff' * 6 + bytes.fromhex(mac) * 16
            
            # Send packet
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(magic_packet, ('255.255.255.255', 9))
            sock.close()
            
            self.logger.info(f"Wake-on-LAN packet sent to {self.target_mac}")
            self.show_notification("Wake-on-LAN", f"Wake packet sent to {self.target_mac}")
        except Exception as e:
            self.logger.error(f"Failed to send wake packet: {str(e)}")
            self.show_notification("Error", f"Failed to send wake packet: {str(e)}")
    
    def sleep_computer(self):
        """Put the local computer to sleep"""
        try:
            self.logger.info("Sending sleep command to system")
            
            if self.os_type == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.os_type == "Darwin":  # macOS
                os.system("pmset sleepnow")
            elif self.os_type == "Linux":
                os.system("systemctl suspend")
            else:
                self.logger.warning(f"Sleep not supported on {self.os_type}")
                self.show_notification("Not Supported", f"Sleep not supported on {self.os_type}")
                return
            
            self.logger.info("Sleep command sent")
        except Exception as e:
            self.logger.error(f"Failed to sleep: {str(e)}")
            self.show_notification("Error", f"Failed to sleep: {str(e)}")
    
    def restart_computer(self):
        """Restart the local computer"""
        try:
            self.logger.info("Sending restart command to system")
            
            if self.os_type == "Windows":
                os.system("shutdown /r /t 5")
            elif self.os_type == "Darwin":  # macOS
                os.system("shutdown -r now")
            elif self.os_type == "Linux":
                os.system("shutdown -r now")
            else:
                self.logger.warning(f"Restart not supported on {self.os_type}")
                self.show_notification("Not Supported", f"Restart not supported on {self.os_type}")
                return
            
            self.logger.info("Restart command sent")
        except Exception as e:
            self.logger.error(f"Failed to restart: {str(e)}")
            self.show_notification("Error", f"Failed to restart: {str(e)}")
    
    def shutdown_computer(self):
        """Shutdown the local computer"""
        try:
            self.logger.info("Sending shutdown command to system")
            
            if self.os_type == "Windows":
                os.system("shutdown /s /t 5")
            elif self.os_type == "Darwin":  # macOS
                os.system("shutdown -h now")
            elif self.os_type == "Linux":
                os.system("shutdown -h now")
            else:
                self.logger.warning(f"Shutdown not supported on {self.os_type}")
                self.show_notification("Not Supported", f"Shutdown not supported on {self.os_type}")
                return
            
            self.logger.info("Shutdown command sent")
        except Exception as e:
            self.logger.error(f"Failed to shutdown: {str(e)}")
            self.show_notification("Error", f"Failed to shutdown: {str(e)}")
    
    #
    # Network functions
    #
    
    def scan_network(self):
        """Scan the network for devices"""
        self.logger.info("Starting network scan")
        self.show_notification("Network Scan", "Scanning network for devices...")
        
        # Run scan in a separate thread to avoid freezing the UI
        threading.Thread(target=self._scan_network_thread).start()
    
    def _scan_network_thread(self):
        """Thread function for network scanning"""
        try:
            # Get network prefix from local IP
            ip_parts = self.server_ip.split('.')
            network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
            
            self.logger.info(f"Scanning network {network_prefix}0/24")
            
            found_devices = []
            
            for i in range(1, 255):
                target_ip = f"{network_prefix}{i}"
                
                # Skip own IP
                if target_ip == self.server_ip:
                    continue
                
                # Try to ping the IP
                ping_cmd = "ping -n 1 -w 500" if self.os_type == "Windows" else "ping -c 1 -W 1"
                response = subprocess.call(f"{ping_cmd} {target_ip}", 
                                         stdout=subprocess.DEVNULL, 
                                         stderr=subprocess.DEVNULL, 
                                         shell=True)
                
                if response == 0:  # Device responded to ping
                    try:
                        # Try to get hostname
                        hostname = socket.gethostbyaddr(target_ip)[0]
                    except socket.herror:
                        hostname = "Unknown"
                    
                    found_devices.append((target_ip, hostname))
                    self.logger.info(f"Found device: {target_ip} ({hostname})")
            
            if found_devices:
                # Show the first few devices found
                devices_str = "\n".join([f"{ip} ({host})" for ip, host in found_devices[:5]])
                if len(found_devices) > 5:
                    devices_str += f"\n... and {len(found_devices) - 5} more"
                
                self.logger.info(f"Found {len(found_devices)} devices on network")
                self.show_notification("Scan Results", f"Found {len(found_devices)} devices:\n{devices_str}")
                
                # Set the first device as target
                if found_devices:
                    self.target_ip = found_devices[0][0]
                    self.get_mac_from_ip(self.target_ip)
            else:
                self.logger.info("No devices found on network")
                self.show_notification("Scan Results", "No devices found")
        
        except Exception as e:
            self.logger.error(f"Network scan failed: {str(e)}")
            self.show_notification("Error", f"Scan failed: {str(e)}")
    
    def get_mac_from_ip(self, ip):
        """Get MAC address from IP address"""
        try:
            self.logger.info(f"Getting MAC address for {ip}")
            
            if self.os_type == "Windows":
                # Use ARP to get MAC
                output = subprocess.check_output(f"arp -a {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        mac = line.split()[1].replace("-", ":")
                        self.target_mac = mac
                        self.logger.info(f"MAC for {ip}: {mac}")
                        return
            
            elif self.os_type == "Darwin":  # macOS
                output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            self.target_mac = parts[3]
                            self.logger.info(f"MAC for {ip}: {self.target_mac}")
                            return
            
            elif self.os_type == "Linux":
                output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            self.target_mac = parts[2]
                            self.logger.info(f"MAC for {ip}: {self.target_mac}")
                            return
            
            self.logger.warning(f"Could not determine MAC for {ip}")
            self.show_notification("MAC Address", f"Could not determine MAC for {ip}")
        
        except Exception as e:
            self.logger.error(f"Failed to get MAC: {str(e)}")
            self.show_notification("Error", f"Failed to get MAC: {str(e)}")
    
    def generate_qr_code(self):
        """Generate a QR code with the connection information"""
        if not QRCODE_AVAILABLE:
            self.show_notification("QR Code Error", "QR code module not available. Install with: pip install qrcode")
            return
            
        if not self.server_running:
            self.show_notification("Server Not Running", "Start the server first")
            return
        
        try:
            self.logger.info("Generating QR code")
            
            # Create connection info for QR code
            connection_info = {
                "app": "WakeMATECompanion",
                "serverIP": self.server_ip,
                "serverPort": self.server_port,
                "targetIP": self.target_ip,
                "targetMAC": self.target_mac
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
            qr_path = os.path.join(self.app_path, "wakemateqr.png")
            img.save(qr_path)
            
            # Open the image with default viewer
            if self.os_type == "Windows":
                os.startfile(qr_path)
            elif self.os_type == "Darwin":  # macOS
                subprocess.call(["open", qr_path])
            elif self.os_type == "Linux":
                subprocess.call(["xdg-open", qr_path])
            
            self.logger.info(f"QR code saved to {qr_path}")
            self.show_notification("QR Code", f"QR code saved to {qr_path}")
        
        except Exception as e:
            self.logger.error(f"Failed to generate QR code: {str(e)}")
            self.show_notification("Error", f"Failed to generate QR code: {str(e)}")
    
    def exit_app(self):
        """Exit the application"""
        self.logger.info("Exiting application")
        
        # Stop auto-start
        self.auto_start_running = False
        
        # Stop server if running
        if self.server_running:
            self.stop_server()
        
        # Stop icon
        if self.icon:
            self.icon.stop()
        
        self.logger.info("Application exited")
        sys.exit(0)


# ----------------------
# Main entry point
# ----------------------

if __name__ == "__main__":
    app = WakeMATECompanion()
    app.run()