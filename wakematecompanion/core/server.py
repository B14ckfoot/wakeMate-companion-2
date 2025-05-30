"""
Server implementation for WakeMATECompanion
"""

import socket
import threading
import json
import logging
import pyautogui

logger = logging.getLogger("WakeMATECompanion")

class WakeMateServer:
    """Server for handling phone app connections"""
    
    def __init__(self, ip, port=7777):
        """Initialize the server
        
        Args:
            ip (str): The IP address to bind to
            port (int, optional): The port to listen on. Defaults to 7777.
        """
        self.ip = ip
        self.port = port
        self.running = False
        self.socket = None
        self.server_thread = None
        self.connected_clients = []
        self.on_notification = None
    
    def set_notification_callback(self, callback):
        """Set the notification callback
        
        Args:
            callback (function): A function that takes title and message parameters
        """
        self.on_notification = callback
    
    def start(self):
        """Start the server"""
        if self.running:
            logger.info("Server is already running")
            return False
        
        try:
            # Start server in a separate thread
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.running = True
            logger.info(f"Server started on {self.ip}:{self.port}")
            
            if self.on_notification:
                self.on_notification("Server Started", f"Listening on {self.ip}:{self.port}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            
            if self.on_notification:
                self.on_notification("Error", f"Failed to start server: {str(e)}")
            
            return False
    
    def stop(self):
        """Stop the server"""
        if not self.running:
            logger.info("Server is not running")
            return True
        
        try:
            # Stop server
            self.running = False
            
            # Close all client connections
            for client_sock, addr in self.connected_clients:
                try:
                    client_sock.close()
                    logger.info(f"Closed connection to {addr[0]}:{addr[1]}")
                except:
                    pass
            
            self.connected_clients = []
            
            # Close server socket
            if self.socket:
                self.socket.close()
                self.socket = None
            
            logger.info("Server stopped")
            
            if self.on_notification:
                self.on_notification("Server Stopped", "Server has been stopped")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to stop server: {str(e)}")
            
            if self.on_notification:
                self.on_notification("Error", f"Failed to stop server: {str(e)}")
            
            return False
    
    def _run_server(self):
        """Server thread function"""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.ip, self.port))
            self.socket.listen(5)
            self.socket.settimeout(1.0)  # Add timeout for accepting connections
            
            logger.info(f"Server listening on {self.ip}:{self.port}")
            
            while self.running:
                try:
                    # Accept connection
                    client_sock, addr = self.socket.accept()
                    
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
                    logger.info(f"New connection from {addr[0]}")
                    
                    if self.on_notification:
                        self.on_notification("New Connection", f"Device at {addr[0]} connected")
                
                except socket.timeout:
                    continue  # Timeout allows checking server_running flag
                except Exception as e:
                    if self.running:  # Only show errors if server should be running
                        logger.error(f"Server error: {str(e)}")
                    break
        
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        
        finally:
            # Clean up if thread exits
            if self.socket:
                self.socket.close()
                self.socket = None
            logger.info("Server stopped")
    
    def _handle_client(self, client_sock, addr):
        """Handle communication with a connected client"""
        client_addr = f"{addr[0]}:{addr[1]}"
        logger.info(f"Handling client connection from {client_addr}")
        
        try:
            # Set a timeout to allow checking server_running flag
            client_sock.settimeout(1.0)
            
            while self.running:
                try:
                    # Receive data
                    data = client_sock.recv(1024)
                    
                    if not data:
                        # Client disconnected
                        logger.info(f"Client {client_addr} disconnected")
                        break
                    
                    # Process command
                    self._process_command(data.decode('utf-8'), client_sock, client_addr)
                
                except socket.timeout:
                    continue
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON from {client_addr}: {str(e)}")
                    response = {"status": "error", "message": "Invalid JSON format"}
                    client_sock.sendall(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    logger.error(f"Error handling client {client_addr}: {str(e)}")
                    break
        
        finally:
            # Remove client from list and close socket
            if (client_sock, addr) in self.connected_clients:
                self.connected_clients.remove((client_sock, addr))
            
            client_sock.close()
            logger.info(f"Connection closed with {client_addr}")
    
    def _process_command(self, command_str, client_sock, client_addr):
        """Process a command from the client"""
        try:
            # Parse JSON command
            command = json.loads(command_str)
            
            # Extract command type and parameters
            cmd_type = command.get("command", "")
            params = command.get("params", {})
            
            logger.info(f"Received command '{cmd_type}' from {client_addr}")
            
            # Execute command and build response
            result = {"status": "success", "message": "Command executed"}
            
            # Simple command processing focuses on basic media controls
            if cmd_type == "media_play_pause":
                self._media_play_pause()
            
            elif cmd_type == "media_next":
                self._media_next()
            
            elif cmd_type == "media_prev":
                self._media_previous()
            
            elif cmd_type == "volume_up":
                self._volume_up()
            
            elif cmd_type == "volume_down":
                self._volume_down()
            
            elif cmd_type == "volume_mute":
                self._volume_mute()
            
            elif cmd_type == "get_status":
                # Return status information
                result = {
                    "status": "success",
                    "data": {
                        "server_ip": self.ip,
                        "server_port": self.port,
                        "connected": True
                    }
                }
            
            else:
                # Unknown command
                logger.warning(f"Unknown command '{cmd_type}' from {client_addr}")
                result = {"status": "error", "message": f"Unknown command: {cmd_type}"}
            
            # Send response
            response = json.dumps(result)
            client_sock.sendall(response.encode('utf-8'))
            
        except json.JSONDecodeError:
            # Invalid JSON
            logger.warning(f"Invalid JSON from {client_addr}")
            response = json.dumps({"status": "error", "message": "Invalid JSON command"})
            client_sock.sendall(response.encode('utf-8'))
        
        except Exception as e:
            # Other errors
            logger.error(f"Error processing command from {client_addr}: {str(e)}")
            response = json.dumps({"status": "error", "message": str(e)})
            client_sock.sendall(response.encode('utf-8'))
    
    # Media control helper functions
    def _media_play_pause(self):
        """Send media play/pause command"""
        try:
            pyautogui.press('playpause')
            logger.info("Media play/pause command sent")
        except Exception as e:
            logger.error(f"Failed to send media play/pause: {str(e)}")
    
    def _media_next(self):
        """Send media next track command"""
        try:
            pyautogui.press('nexttrack')
            logger.info("Media next track command sent")
        except Exception as e:
            logger.error(f"Failed to send media next track: {str(e)}")
    
    def _media_previous(self):
        """Send media previous track command"""
        try:
            pyautogui.press('prevtrack')
            logger.info("Media previous track command sent")
        except Exception as e:
            logger.error(f"Failed to send media previous track: {str(e)}")
    
    def _volume_up(self):
        """Increase volume"""
        try:
            pyautogui.press('volumeup')
            logger.info("Volume up command sent")
        except Exception as e:
            logger.error(f"Failed to send volume up: {str(e)}")
    
    def _volume_down(self):
        """Decrease volume"""
        try:
            pyautogui.press('volumedown')
            logger.info("Volume down command sent")
        except Exception as e:
            logger.error(f"Failed to send volume down: {str(e)}")
    
    def _volume_mute(self):
        """Mute/unmute volume"""
        try:
            pyautogui.press('volumemute')
            logger.info("Volume mute command sent")
        except Exception as e:
            logger.error(f"Failed to send volume mute: {str(e)}")