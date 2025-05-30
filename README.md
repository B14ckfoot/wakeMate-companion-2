# WakeMATECompanion

A modular cross-platform utility for remote system control from mobile devices.

## Features

- **Modular architecture** with Python core and native modules for OS-specific features
- **System tray interface** for easy server management
- **Remote control** capabilities:
  - Media controls (play/pause, next/previous, volume)
  - System power controls (shutdown, restart, sleep)
  - Mouse and keyboard input
  - Wake-on-LAN functionality
- **QR code pairing** for easy mobile app connection
- **Cross-platform support** for Windows, macOS, and Linux
- **Native notifications** on supported platforms

## Requirements

- Python 3.6+
- Required Python packages (install with `pip install -r requirements.txt`):
  - pystray
  - Pillow
  - pyautogui
  - qrcode
  - plyer

## Installation

1. Clone or download this repository: