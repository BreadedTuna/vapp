cd ~

cd vapp
python3 -m venv vapp
source vapp/bin

pip install discord.py discord asyncio psutil pyautogui paperclip google-generativeai zenity

sudo apt install espeak
sudo apt install ffmpeg
sudo apt install zenity

echo "Installation Complete"
echo "You may now run the bot.py with 'python3 bot.py'."
