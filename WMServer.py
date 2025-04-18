import sys
import socket
import platform
import threading
import subprocess
import time
import ipaddress
import qrcode
import json
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import pyautogui
import io
import os

class WakeMATECompanion:
    def __init__(self):
        self.os_type = platform.system()
        self.connected = False
        self.target_ip = None
        self.target_mac = None
        self.icon = None
        self.app_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(self.app_path, "icon.png")
        self.create_default_icon()
        
        # Server configuration
        self.server_ip = self.get_local_ip()
        self.server_port = 7777  # Port for phone app communication
        self.server_running = False
        self.server_socket = None
        self.connected_clients = []
        
    def create_default_icon(self):
        """Create a default icon if one doesn't exist"""
        if not os.path.exists(self.icon_path):
            # Create a simple icon - a blue circle
            img = Image.new('RGB', (64, 64), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            d.ellipse((5, 5, 59, 59), fill=(0, 120, 212))
            img.save(self.icon_path)
    
    def get_local_ip(self):
        """Get the local IP address"""
        try:
            # This creates a socket that doesn't actually connect
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"  # Fallback to localhost
    
    def create_system_tray(self):
        """Create the system tray icon and menu"""
        icon_image = Image.open(self.icon_path)
        
        menu = (
            item('Status', self.show_status),
            item('Network', (
                item('Scan for Devices', self.scan_network),
                item('Generate QR Code', self.generate_qr_code)
            )),
            item('Phone Connection', (
                item('Start Server', self.start_server),
                item('Stop Server', self.stop_server),
                item('Show Connection Info', self.show_connection_info)
            )),
            item('Exit', self.exit_app)
        )
        
        self.icon = pystray.Icon("WakeMATE", icon_image, "WakeMATE Companion", menu)
        return self.icon
    
    def run(self):
        """Run the application"""
        icon = self.create_system_tray()
        icon.run()
    
    def show_status(self):
        """Show the current connection status"""
        status = f"Connected: {self.connected}\n"
        status += f"Target IP: {self.target_ip}\n"
        status += f"Target MAC: {self.target_mac}\n"
        status += f"OS: {self.os_type}\n"
        status += f"Server Running: {self.server_running}\n"
        status += f"Server IP: {self.server_ip}\n"
        status += f"Server Port: {self.server_port}\n"
        status += f"Connected Clients: {len(self.connected_clients)}"
        self.show_notification("WakeMATE Status", status)
    
    def show_notification(self, title, message):
        """Show a system notification"""
        if self.icon:
            self.icon.notify(message, title)
    
    # Media control functions
    def media_play_pause(self):
        """Send media play/pause command"""
        pyautogui.press('playpause')
        self.show_notification("Media Control", "Play/Pause pressed")
    
    def media_next(self):
        """Send media next track command"""
        pyautogui.press('nexttrack')
        self.show_notification("Media Control", "Next Track pressed")
    
    def media_previous(self):
        """Send media previous track command"""
        pyautogui.press('prevtrack')
        self.show_notification("Media Control", "Previous Track pressed")
    
    def volume_up(self):
        """Increase volume"""
        pyautogui.press('volumeup')
        self.show_notification("Volume Control", "Volume increased")
    
    def volume_down(self):
        """Decrease volume"""
        pyautogui.press('volumedown')
        self.show_notification("Volume Control", "Volume decreased")
    
    def volume_mute(self):
        """Mute/unmute volume"""
        pyautogui.press('volumemute')
        self.show_notification("Volume Control", "Volume muted/unmuted")
    
    # System control functions
    def wake_computer(self):
        """Wake the target computer using Wake-on-LAN"""
        if not self.target_mac:
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
            
            self.show_notification("Wake-on-LAN", f"Wake packet sent to {self.target_mac}")
        except Exception as e:
            self.show_notification("Error", f"Failed to send wake packet: {str(e)}")
    
    def sleep_computer(self):
        """Put the local computer to sleep"""
        try:
            if self.os_type == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif self.os_type == "Darwin":  # macOS
                os.system("pmset sleepnow")
            elif self.os_type == "Linux":
                os.system("systemctl suspend")
            
            self.show_notification("System Control", "Sleep command sent")
        except Exception as e:
            self.show_notification("Error", f"Failed to sleep: {str(e)}")
    
    def restart_computer(self):
        """Restart the local computer"""
        try:
            if self.os_type == "Windows":
                os.system("shutdown /r /t 5")
            elif self.os_type in ["Darwin", "Linux"]:  # macOS or Linux
                os.system("shutdown -r now")
            
            self.show_notification("System Control", "Restart command sent")
        except Exception as e:
            self.show_notification("Error", f"Failed to restart: {str(e)}")
    
    def shutdown_computer(self):
        """Shutdown the local computer"""
        try:
            if self.os_type == "Windows":
                os.system("shutdown /s /t 5")
            elif self.os_type in ["Darwin", "Linux"]:  # macOS or Linux
                os.system("shutdown -h now")
            
            self.show_notification("System Control", "Shutdown command sent")
        except Exception as e:
            self.show_notification("Error", f"Failed to shutdown: {str(e)}")
    
    # Network functions
    def scan_network(self):
        """Scan the network for devices"""
        self.show_notification("Network Scan", "Scanning network for devices...")
        
        # Run scan in a separate thread to avoid freezing the UI
        threading.Thread(target=self._scan_network_thread).start()
    
    def _scan_network_thread(self):
        """Thread function for network scanning"""
        try:
            # Get network prefix from local IP
            ip_parts = self.server_ip.split('.')
            network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."
            
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
            
            if found_devices:
                # Show the first few devices found
                devices_str = "\n".join([f"{ip} ({host})" for ip, host in found_devices[:5]])
                if len(found_devices) > 5:
                    devices_str += f"\n... and {len(found_devices) - 5} more"
                
                self.show_notification("Scan Results", f"Found {len(found_devices)} devices:\n{devices_str}")
                
                # Set the first device as target
                if found_devices:
                    self.target_ip = found_devices[0][0]
                    self.get_mac_from_ip(self.target_ip)
            else:
                self.show_notification("Scan Results", "No devices found")
        
        except Exception as e:
            self.show_notification("Error", f"Scan failed: {str(e)}")
    
    def get_mac_from_ip(self, ip):
        """Get MAC address from IP address"""
        try:
            if self.os_type == "Windows":
                # Use ARP to get MAC
                output = subprocess.check_output(f"arp -a {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        mac = line.split()[1].replace("-", ":")
                        self.target_mac = mac
                        return
            
            elif self.os_type == "Darwin":  # macOS
                output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            self.target_mac = parts[3]
                            return
            
            elif self.os_type == "Linux":
                output = subprocess.check_output(f"arp -n {ip}", shell=True).decode('utf-8')
                for line in output.splitlines():
                    if ip in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            self.target_mac = parts[2]
                            return
            
            self.show_notification("MAC Address", f"Could not determine MAC for {ip}")
        
        except Exception as e:
            self.show_notification("Error", f"Failed to get MAC: {str(e)}")
    
    def set_ip_manually(self):
        """
        Set IP address manually
        Note: In a real application, this would open a dialog
        Here we're just simulating it
        """
        # In a real app, you would show a dialog here
        # For this example, we'll just set a sample IP
        sample_ip = "192.168.1.100"
        self.target_ip = sample_ip
        self.get_mac_from_ip(sample_ip)
        self.show_notification("IP Set", f"Target IP set to {sample_ip}")
    
    def generate_qr_code(self):
        """Generate a QR code with the connection information"""
        if not self.server_running:
            self.show_notification("Server Not Running", "Start the server first")
            return
        
        try:
            # Create connection info for QR code
            connection_info = {
                "app": "WakeMATE",
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
            
            self.show_notification("QR Code", f"QR code saved to {qr_path}")
        
        except Exception as e:
            self.show_notification("Error", f"Failed to generate QR code: {str(e)}")
    
    # Phone communication functions
    def start_server(self):
        """Start the server for phone app communication"""
        if self.server_running:
            self.show_notification("Server", "Server is already running")
            return
        
        try:
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True  # Thread will close when main app exits
            self.server_thread.start()
            
            self.server_running = True
            self.show_notification("Server Started", f"Listening on {self.server_ip}:{self.server_port}")
        
        except Exception as e:
            self.show_notification("Error", f"Failed to start server: {str(e)}")
    
    def _run_server(self):
        """Server thread function"""
        try:
            # Create socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(5)
            
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
                    
                    # Show notification
                    self.show_notification("New Connection", f"Phone at {addr[0]} connected")
                
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.server_running:  # Only show errors if server should be running
                        self.show_notification("Server Error", str(e))
                    break
        
        except Exception as e:
            self.show_notification("Server Error", str(e))
        
        finally:
            # Clean up if thread exits
            if self.server_socket:
                self.server_socket.close()
    
    def _handle_client(self, client_sock, addr):
        """Handle communication with a connected phone"""
        try:
            # Set a timeout to allow checking server_running flag
            client_sock.settimeout(1.0)
            
            while self.server_running:
                try:
                    # Receive data
                    data = client_sock.recv(1024)
                    
                    if not data:
                        # Client disconnected
                        break
                    
                    # Process command
                    self._process_command(data.decode('utf-8'), client_sock)
                
                except socket.timeout:
                    continue
                except Exception as e:
                    self.show_notification("Client Error", str(e))
                    break
        
        finally:
            # Remove client from list and close socket
            if (client_sock, addr) in self.connected_clients:
                self.connected_clients.remove((client_sock, addr))
            
            client_sock.close()
            self.show_notification("Connection Closed", f"Phone at {addr[0]} disconnected")
    
    def _process_command(self, command_str, client_sock):
        """Process a command from the phone app"""
        try:
            # Parse JSON command
            command = json.loads(command_str)
            
            # Extract command type and parameters
            cmd_type = command.get("command", "")
            params = command.get("params", {})
            
            # Execute command
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
                        "connected": self.connected
                    }
                }
            
            else:
                # Unknown command
                result = {"status": "error", "message": f"Unknown command: {cmd_type}"}
            
            # Send response
            response = json.dumps(result)
            client_sock.sendall(response.encode('utf-8'))
        
        except json.JSONDecodeError:
            # Invalid JSON
            response = json.dumps({"status": "error", "message": "Invalid JSON command"})
            client_sock.sendall(response.encode('utf-8'))
        
        except Exception as e:
            # Other errors
            response = json.dumps({"status": "error", "message": str(e)})
            client_sock.sendall(response.encode('utf-8'))
    
    def stop_server(self):
        """Stop the server"""
        if not self.server_running:
            self.show_notification("Server", "Server is not running")
            return
        
        try:
            # Stop server
            self.server_running = False
            
            # Close all client connections
            for client_sock, _ in self.connected_clients:
                try:
                    client_sock.close()
                except:
                    pass
            
            self.connected_clients = []
            
            # Close server socket
            if self.server_socket:
                self.server_socket.close()
                self.server_socket = None
            
            self.show_notification("Server Stopped", "Server has been stopped")
        
        except Exception as e:
            self.show_notification("Error", f"Failed to stop server: {str(e)}")
    
    def show_connection_info(self):
        """Show connection information for phone app"""
        if not self.server_running:
            self.show_notification("Server Not Running", "Start the server first")
            return
        
        info = f"Server IP: {self.server_ip}\n"
        info += f"Server Port: {self.server_port}\n\n"
        info += "Scan the QR code to connect from phone app\n"
        info += "or manually enter the connection details."
        
        self.show_notification("Connection Info", info)
    
    def exit_app(self):
        """Exit the application"""
        # Stop server if running
        if self.server_running:
            self.stop_server()
        
        # Stop icon
        if self.icon:
            self.icon.stop()
        
        sys.exit(0)

if __name__ == "__main__":
    app = WakeMATECompanion()
    app.run()