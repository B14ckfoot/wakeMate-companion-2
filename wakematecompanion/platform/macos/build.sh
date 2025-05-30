#!/bin/bash
# macOS build script for WakeMATECompanion native modules

echo "Building macOS native modules..."

# Create output directory
mkdir -p ../../bin/macos

# Build notifications library
echo "Building libwm_notifications.dylib..."
clang -dynamiclib -o ../../bin/macos/libwm_notifications.dylib notifications.m \
    -framework Foundation \
    -framework AppKit \
    -framework UserNotifications \
    -lobjc

if [ $? -ne 0 ]; then
    echo "Failed to build libwm_notifications.dylib"
    exit 1
fi

echo "macOS native modules built successfully."