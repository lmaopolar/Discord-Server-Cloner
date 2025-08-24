# Discord Server Template Cloner

A Python Discord bot that can clone any Discord server template into an existing server with a slash command.  
Made by Polar.

## Features
- Clone roles, categories, and channels from any Discord template.
- Preserves channel permissions, slowmode, NSFW flags, and voice channel settings.
- Slash command `/apply_template` to trigger cloning.
- Includes `/ping` for health check.

## Setup

1. Clone this repository:
   git clone https://github.com/lmaopolar/discord-server-cloner.git
   cd discord-server-cloner

2. Install requirements:
   pip install -r requirements.txt

3. Edit `bot.py` and replace:
   TOKEN = "YOUR_TOKEN_HERE"
   with your bot token from the Discord Developer Portal.

4. Run the bot:
   python bot.py

## Usage

1. Invite your bot to a server with Administrator permissions (or at least Manage Roles, Manage Channels).
2. In that server, type:
   /apply_template template:<discord.new/XXXX>
   Replace `<discord.new/XXXX>` with a valid template link or code.
3. The bot will rebuild the server’s structure based on that template.

## Limitations
- Does not clone bots, emojis, stickers, webhooks, boosts, or integrations.  
- Member-specific overwrites are skipped.  
- Some advanced channel types may need manual tweaks.  

## Requirements
- Python 3.8+
- discord.py 2.3+
- aiohttp

Install with:
   pip install discord.py aiohttp

## License
MIT License. Free to use, modify, and share.  
Made by Polar.