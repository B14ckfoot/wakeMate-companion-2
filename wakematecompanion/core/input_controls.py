"""
Input control utilities for WakeMATECompanion
"""

import platform
import logging
import subprocess

logger = logging.getLogger("WakeMATECompanion")

def move_mouse(dx, dy):
    """Move the mouse cursor by the given delta x and y
    
    Args:
        dx (int): Horizontal movement (positive is right)
        dy (int): Vertical movement (positive is down)
    """
    try:
        import pyautogui
        # Get current position
        current_x, current_y = pyautogui.position()
        # Calculate new position
        new_x = current_x + int(dx)
        new_y = current_y + int(dy)
        # Move to new position
        pyautogui.moveTo(new_x, new_y)
        logger.info(f"Mouse moved by ({dx}, {dy})")
    except Exception as e:
        logger.error(f"Failed to move mouse: {str(e)}")
        raise

def click_mouse(button="left"):
    """Click the mouse
    
    Args:
        button (str): Which button to click ("left", "right", or "middle")
    """
    try:
        import pyautogui
        pyautogui.click(button=button)
        logger.info(f"Mouse {button} click")
    except Exception as e:
        logger.error(f"Failed to click mouse: {str(e)}")
        raise

def scroll_mouse(amount):
    """Scroll the mouse wheel
    
    Args:
        amount (int): Scroll amount (positive for up, negative for down)
    """
    try:
        import pyautogui
        pyautogui.scroll(int(amount))
        logger.info(f"Mouse scrolled by {amount}")
    except Exception as e:
        logger.error(f"Failed to scroll mouse: {str(e)}")
        raise

def type_text(text):
    """Type text
    
    Args:
        text (str): Text to type
    """
    try:
        import pyautogui
        pyautogui.write(text)
        logger.info(f"Typed text: {text[:10]}{'...' if len(text) > 10 else ''}")
    except Exception as e:
        logger.error(f"Failed to type text: {str(e)}")
        raise

def press_key(key):
    """Press a special key
    
    Args:
        key (str): Key to press (e.g., "enter", "escape", "tab")
    """
    try:
        import pyautogui
        pyautogui.press(key)
        logger.info(f"Special key {key} pressed")
    except Exception as e:
        logger.error(f"Failed to press special key: {str(e)}")
        raise