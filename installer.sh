#!/bin/bash

# Ensure script is run from the repository directory
if [ ! -f "bot.py" ]; then
    echo "Error: Please run this script from the vapp repository directory."
    exit 1
fi

# Set up the virtual environment in a separate directory (e.g., .venv)
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install --upgrade pip  # Ensure pip is up to date
pip install discord.py discord asyncio psutil pyautogui paperclip google-generativeai zenity

# Install system-level dependencies
sudo apt-get install -y python3-tk python3-dev
sudo apt update
sudo apt install -y espeak ffmpeg zenity

# Notify user of successful installation
echo "Installation Complete."
echo "Running file with 'python3 bot.py'"

cd ~/vapp
python3 bot.py

echo "Running..."
