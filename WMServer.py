[PATCHED FULL WMServer.py — with True Original Structure + Fixes]

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

        self.server_ip = self.get_local_ip()
        self.server_port = 7777
        self.server_running = False
        self.server_socket = None
        self.connected_clients = []
        self.last_conn_notify = 0

    def create_default_icon(self):
        if not os.path.exists(self.icon_path):
            img = Image.new('RGB', (64, 64), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            d.ellipse((5, 5, 59, 59), fill=(0, 120, 212))
            img.save(self.icon_path)

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def run(self):
        self.start_server()
        icon = self.create_system_tray()
        icon.run()

    def create_system_tray(self):
        icon_image = Image.open(self.icon_path)
        menu = pystray.Menu(
            item('Status', self.show_status),
            item('Exit', self.exit_app)
        )
        self.icon = pystray.Icon("WakeMATE", icon_image, "WakeMATE Companion", menu)
        return self.icon

    def show_notification(self, title, message):
        if self.icon:
            self.icon.notify(message, title)

    def show_status(self):
        status = f"Connected: {self.connected}\nTarget IP: {self.target_ip}\nTarget MAC: {self.target_mac}\nOS: {self.os_type}\nServer Running: {self.server_running}\nServer IP: {self.server_ip}\nServer Port: {self.server_port}\nConnected Clients: {len(self.connected_clients)}"
        self.show_notification("WakeMATE Status", status)

    def _safe_pyautogui(self, action, *args, **kwargs):
        try:
            getattr(pyautogui, action)(*args, **kwargs)
        except Exception as e:
            self.show_notification("Error", f"PyAutoGUI error: {str(e)}")

    def sleep_computer(self):
        try:
            if self.os_type == "Windows":
                subprocess.call(["rundll32.exe", "powrprof.dll,SetSuspendState", "Sleep"])
            elif self.os_type == "Darwin":
                os.system("pmset sleepnow")
            elif self.os_type == "Linux":
                os.system("systemctl suspend")
            self.show_notification("System Control", "Sleep command sent")
        except Exception as e:
            self.show_notification("Error", f"Sleep error: {str(e)}")

    def _ping_target_ip(self):
        if not self.target_ip:
            return False
        try:
            ping_cmd = "ping -n 1 -w 1000" if self.os_type == "Windows" else "ping -c 1 -W 1"
            response = subprocess.call(f"{ping_cmd} {self.target_ip}", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            return response == 0
        except Exception:
            return False

    def start_server(self):
        if self.server_running:
            return
        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.server_running = True

    def _run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(5)
            while self.server_running:
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock, addr)).start()
                self.connected_clients.append((client_sock, addr))
                now = time.time()
                if now - self.last_conn_notify > 60:
                    self.show_notification("New Connection", f"Client {addr[0]} connected")
                    self.last_conn_notify = now
        except Exception as e:
            self.show_notification("Server Error", str(e))
        finally:
            if self.server_socket:
                self.server_socket.close()

    def _handle_client(self, client_sock, addr):
        try:
            data = client_sock.recv(4096)
            if data:
                command = json.loads(data.decode('utf-8'))
                self._execute_command(command)
        except Exception as e:
            pass
        finally:
            if (client_sock, addr) in self.connected_clients:
                self.connected_clients.remove((client_sock, addr))
            client_sock.close()

    def _execute_command(self, command):
        cmd_type = command.get("command")
        if cmd_type == "sleep":
            self.sleep_computer()
        elif cmd_type == "get_status":
            result = {"connected": self._ping_target_ip()}
        elif cmd_type == "media_play_pause":
            self._safe_pyautogui('press', 'playpause')
        elif cmd_type == "media_next":
            self._safe_pyautogui('press', 'nexttrack')
        elif cmd_type == "media_prev":
            self._safe_pyautogui('press', 'prevtrack')
        elif cmd_type == "volume_up":
            self._safe_pyautogui('press', 'volumeup')
        elif cmd_type == "volume_down":
            self._safe_pyautogui('press', 'volumedown')
        elif cmd_type == "volume_mute":
            self._safe_pyautogui('press', 'volumemute')

    def exit_app(self):
        if self.server_running:
            self.server_running = False
            for sock, _ in self.connected_clients:
                try: sock.close()
                except: pass
            if self.server_socket:
                self.server_socket.close()
        if self.icon:
            self.icon.stop()
        sys.exit(0)

if __name__ == "__main__":
    app = WakeMATECompanion()
    app.run()