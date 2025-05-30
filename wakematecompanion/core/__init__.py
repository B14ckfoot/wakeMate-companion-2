"""
Server implementation for WakeMATECompanion
"""

import socket
import threading
import json
import logging
import time
from typing import Callable, Optional, Dict, Any

from .media_controls import MediaControls

logger = logging.getLogger("WakeMATECompanion")

class WakeMateServer:
    """Server for handling phone app connections"""
    
    def __init__(self, ip: str, port: int = 7777):
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
        self.on_notification: Optional[Callable[[str, str], None]] = None
        self.media_controls = MediaControls()
        
        # Commands registry - maps command names to handler functions
        self.commands = {
            'get_status': self._handle_get_status,
            'media_play_pause': self._handle_media_play_pause,
            'media_next': self._handle_media_next,
            'media_prev': self._handle_media_previous,
            'volume_up': self._handle_volume_up,
            'volume_down': self._handle_volume_down,
            'volume_mute': self._handle_volume_mute,
            'shutdown': self._handle_shutdown,
            'restart': self._handle_restart,
            'sleep': self._handle_sleep,
            'wake': self._handle_wake,
            'mouse_move': self._handle_mouse_move,
            'mouse_click': self._handle_mouse_click,
            'mouse_scroll': self._handle_mouse_scroll,
            'keyboard_input': self._handle_keyboard_input,
            'keyboard_special': self._handle_keyboard_special,
        }
    
    def set_notification_callback(self, callback: Callable[[str, str], None]):
        """Set the notification callback
        
        Args:
            callback (function): A function that takes title and message parameters
        """
        self.on_notification = callback
    
    def start(self) -> bool:
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
    
    def stop(self) -> bool:
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
    
    def _handle_client(self, client_sock: socket.socket, addr: tuple):
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
                    logger.warning(f"Invalid JSON from {client_addr}")
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
    
    def _process_command(self, command_str: str, client_sock: socket.socket, client_addr: str):
        """Process a command from the client"""
        try:
            # Parse JSON command
            command = json.loads(command_str)
            
            # Extract command type and parameters
            cmd_type = command.get("command", "")
            params = command.get("params", {})
            
            logger.info(f"Received command '{cmd_type}' from {client_addr}")
            
            # Find and execute the command handler
            handler = self.commands.get(cmd_type)
            if handler:
                result = handler(params, client_addr)
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
    
    # Command handlers
    def _handle_get_status(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle get_status command"""
        return {
            "status": "success",
            "data": {
                "server_ip": self.ip,
                "server_port": self.port,
                "connected": True,
                "version": "2.0.0",
            }
        }
    
    def _handle_media_play_pause(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle media_play_pause command"""
        try:
            self.media_controls.play_pause()
            logger.info("Media play/pause command executed")
            return {"status": "success", "message": "Media play/pause command executed"}
        except Exception as e:
            logger.error(f"Failed to execute media play/pause: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_media_next(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle media_next command"""
        try:
            self.media_controls.next_track()
            logger.info("Media next track command executed")
            return {"status": "success", "message": "Media next track command executed"}
        except Exception as e:
            logger.error(f"Failed to execute media next track: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_media_previous(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle media_prev command"""
        try:
            self.media_controls.previous_track()
            logger.info("Media previous track command executed")
            return {"status": "success", "message": "Media previous track command executed"}
        except Exception as e:
            logger.error(f"Failed to execute media previous track: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_volume_up(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle volume_up command"""
        try:
            self.media_controls.volume_up()
            logger.info("Volume up command executed")
            return {"status": "success", "message": "Volume up command executed"}
        except Exception as e:
            logger.error(f"Failed to execute volume up: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_volume_down(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle volume_down command"""
        try:
            self.media_controls.volume_down()
            logger.info("Volume down command executed")
            return {"status": "success", "message": "Volume down command executed"}
        except Exception as e:
            logger.error(f"Failed to execute volume down: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_volume_mute(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle volume_mute command"""
        try:
            self.media_controls.volume_mute()
            logger.info("Volume mute command executed")
            return {"status": "success", "message": "Volume mute command executed"}
        except Exception as e:
            logger.error(f"Failed to execute volume mute: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_shutdown(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle shutdown command"""
        try:
            from .system_controls import shutdown
            shutdown()
            logger.info("Shutdown command executed")
            return {"status": "success", "message": "Shutdown command executed"}
        except Exception as e:
            logger.error(f"Failed to execute shutdown: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_restart(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle restart command"""
        try:
            from .system_controls import restart
            restart()
            logger.info("Restart command executed")
            return {"status": "success", "message": "Restart command executed"}
        except Exception as e:
            logger.error(f"Failed to execute restart: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_sleep(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle sleep command"""
        try:
            from .system_controls import sleep
            sleep()
            logger.info("Sleep command executed")
            return {"status": "success", "message": "Sleep command executed"}
        except Exception as e:
            logger.error(f"Failed to execute sleep: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_wake(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle wake command"""
        try:
            from .utils.wol import send_magic_packet
            
            mac = params.get("mac")
            if not mac:
                return {"status": "error", "message": "MAC address is required"}
            
            send_magic_packet(mac)
            logger.info(f"Wake command executed for MAC: {mac}")
            return {"status": "success", "message": f"Wake command sent to {mac}"}
        except Exception as e:
            logger.error(f"Failed to execute wake: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_mouse_move(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle mouse_move command"""
        try:
            dx = params.get("dx", 0)
            dy = params.get("dy", 0)
            
            from .input_controls import move_mouse
            move_mouse(dx, dy)
            
            return {"status": "success", "message": "Mouse moved"}
        except Exception as e:
            logger.error(f"Failed to move mouse: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_mouse_click(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle mouse_click command"""
        try:
            button = params.get("button", "left")
            
            from .input_controls import click_mouse
            click_mouse(button)
            
            return {"status": "success", "message": f"Mouse {button} click"}
        except Exception as e:
            logger.error(f"Failed to click mouse: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_mouse_scroll(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle mouse_scroll command"""
        try:
            amount = params.get("amount", 0)
            
            from .input_controls import scroll_mouse
            scroll_mouse(amount)
            
            return {"status": "success", "message": "Mouse scrolled"}
        except Exception as e:
            logger.error(f"Failed to scroll mouse: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_keyboard_input(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle keyboard_input command"""
        try:
            text = params.get("text", "")
            if not text:
                return {"status": "error", "message": "Text is required"}
            
            from .input_controls import type_text
            type_text(text)
            
            return {"status": "success", "message": "Text typed"}
        except Exception as e:
            logger.error(f"Failed to type text: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _handle_keyboard_special(self, params: Dict[str, Any], client_addr: str) -> Dict[str, Any]:
        """Handle keyboard_special command"""
        try:
            key = params.get("key", "")
            if not key:
                return {"status": "error", "message": "Key is required"}
            
            from .input_controls import press_key
            press_key(key)
            
            return {"status": "success", "message": f"Special key {key} pressed"}
        except Exception as e:
            logger.error(f"Failed to press special key: {str(e)}")
            return {"status": "error", "message": str(e)}