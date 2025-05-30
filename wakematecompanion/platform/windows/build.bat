@echo off
REM Windows build script for WakeMATECompanion native modules

echo Building Windows native modules...

REM Create output directory
mkdir ..\..\bin\windows

REM Check if WinToast is available
if not exist "wintoast" (
    echo WinToast not found. Downloading...
    REM Use PowerShell to download WinToast
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/mohabouje/WinToast/archive/refs/heads/master.zip' -OutFile 'wintoast.zip'; Expand-Archive -Path 'wintoast.zip' -DestinationPath '.' -Force; Rename-Item -Path 'WinToast-master' -NewName 'wintoast'}"
)

REM Build notifications DLL
echo Building notifications.dll...
cl.exe /EHsc /LD /I"wintoast/src" notifications.cpp /Fe..\..\bin\windows\wm_notifications.dll user32.lib shell32.lib

if %ERRORLEVEL% NEQ 0 (
    echo Failed to build notifications.dll
    exit /b %ERRORLEVEL%
)

echo Windows native modules built successfully.