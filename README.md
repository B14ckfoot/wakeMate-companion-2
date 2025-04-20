# WakeMATECompanion

A streamlined, cross-platform utility for remote system control from mobile devices.

## Features

- **Simple System Tray Interface**: Focus on server status and QR code generation
- **Remote Media Control**: Play/pause, next/previous track, and volume controls
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Mobile Integration**: Connect with mobile apps via QR code

## Requirements

- Python 3.6+
- Required Python packages (install with `pip install -r requirements.txt`):
  - pystray
  - Pillow
  - pyautogui
  - qrcode (for QR code generation)

## Installation

1. Clone or download this repository
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python -m wakematecompanion
   ```

## Usage

1. After starting the application, WakeMATECompanion will run in the system tray/menu bar
2. The system tray menu provides the following options:
   - **Server Status**: Shows whether the server is online or offline
   - **Toggle Server**: Start or stop the server
   - **Generate QR Code**: Create a QR code that contains connection information for the mobile app
   - **Exit**: Close the application
3. Scan the QR code with your mobile app to connect to your computer

## Troubleshooting

If you encounter issues:

1. Check the logs: Look at the `wakeMate.log` file in the application directory
2. Ensure your firewall allows connections on port 7777
3. Make sure your phone and computer are on the same network

## Mobile App

The WakeMATECompanion mobile app is available for:
- Android: [Coming soon]
- iOS: [Coming soon]

You can connect any compatible remote control app to WakeMATECompanion by using the server IP and port.

## Development

The application follows a modular structure:

- `main.py`: Entry point for the application
- `server.py`: Server implementation for phone connections
- `system_tray.py`: Streamlined system tray interface
- `qr_generator.py`: QR code generation functionality
- `network_utils.py`: Network utilities (IP/MAC detection)
- `logging_config.py`: Centralized logging configuration

To contribute to the project, please follow standard Python coding conventions (PEP 8).

## License

This software is provided as-is under the MIT License.