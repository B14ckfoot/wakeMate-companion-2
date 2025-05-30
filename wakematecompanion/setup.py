from setuptools import setup, find_packages
import os
import platform
import subprocess
from pathlib import Path

# Build native modules based on platform
system = platform.system()
print(f"Detected platform: {system}")

if system == 'Windows':
    build_script = Path('platform/windows/build.bat')
    if build_script.exists():
        print("Building Windows native modules...")
        subprocess.call([str(build_script)])
elif system == 'Darwin':  # macOS
    build_script = Path('platform/macos/build.sh')
    if build_script.exists():
        print("Building macOS native modules...")
        subprocess.call(['bash', str(build_script)])

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wakematecompanion",
    version="2.0.0",
    author="WakeMATECompanion Team",
    author_email="support@wakemate.example.com",
    description="A modular cross-platform utility for remote system control",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/wakematecompanion",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pystray>=0.19.0",
        "Pillow>=9.0.0",
        "pyautogui>=0.9.53",
        "qrcode>=7.3.1",
        "plyer>=2.0.0",  # For fallback notifications
    ],
    entry_points={
        "console_scripts": [
            "wakematecompanion=wakematecompanion.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["bin/*/*", "resources/icons/*"],
    },
)