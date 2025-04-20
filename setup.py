from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wakematecompanion",
    version="1.0.0",
    author="WakeMATECompanion Team",
    author_email="support@wakemate.example.com",
    description="A streamlined cross-platform utility for remote system control",
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
    ],
    entry_points={
        "console_scripts": [
            "wakematecompanion=wakematecompanion.main:main",
        ],
    },
)
