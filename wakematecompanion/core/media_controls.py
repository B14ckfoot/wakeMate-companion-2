"""
Media control utilities for WakeMATECompanion
"""

import platform
import logging
import subprocess

logger = logging.getLogger("WakeMATECompanion")

class MediaControls:
    """Cross-platform media controls"""
    
    def __init__(self):
        """Initialize media controls"""
        self.system = platform.system()
    
    def play_pause(self):
        """Play/pause media"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('playpause')
            elif self.system == "Darwin":  # macOS
                script = """
                tell application "System Events"
                    key code 16 using {command down}
                end tell
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify', 
                               '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.PlayPause'], 
                               check=False)
            logger.info("Media play/pause command sent")
        except Exception as e:
            logger.error(f"Failed to execute play/pause: {str(e)}")
            raise
    
    def next_track(self):
        """Next track"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('nexttrack')
            elif self.system == "Darwin":  # macOS
                script = """
                tell application "System Events"
                    key code 17 using {command down}
                end tell
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify', 
                               '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.Next'], 
                               check=False)
            logger.info("Media next track command sent")
        except Exception as e:
            logger.error(f"Failed to execute next track: {str(e)}")
            raise
    
    def previous_track(self):
        """Previous track"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('prevtrack')
            elif self.system == "Darwin":  # macOS
                script = """
                tell application "System Events"
                    key code 18 using {command down}
                end tell
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify', 
                               '/org/mpris/MediaPlayer2', 'org.mpris.MediaPlayer2.Player.Previous'], 
                               check=False)
            logger.info("Media previous track command sent")
        except Exception as e:
            logger.error(f"Failed to execute previous track: {str(e)}")
            raise
    
    def volume_up(self):
        """Increase volume"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('volumeup')
            elif self.system == "Darwin":  # macOS
                script = """
                set volume output volume (output volume of (get volume settings) + 10) --100%
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '5%+'], check=False)
            logger.info("Volume up command sent")
        except Exception as e:
            logger.error(f"Failed to execute volume up: {str(e)}")
            raise
    
    def volume_down(self):
        """Decrease volume"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('volumedown')
            elif self.system == "Darwin":  # macOS
                script = """
                set volume output volume (output volume of (get volume settings) - 10) --100%
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', '5%-'], check=False)
            logger.info("Volume down command sent")
        except Exception as e:
            logger.error(f"Failed to execute volume down: {str(e)}")
            raise
    
    def volume_mute(self):
        """Mute/unmute volume"""
        try:
            if self.system == "Windows":
                import pyautogui
                pyautogui.press('volumemute')
            elif self.system == "Darwin":  # macOS
                script = """
                set volume with output muted
                """
                subprocess.run(['osascript', '-e', script], check=True)
            elif self.system == "Linux":
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', 'toggle'], check=False)
            logger.info("Volume mute command sent")
        except Exception as e:
            logger.error(f"Failed to execute volume mute: {str(e)}")
            raise