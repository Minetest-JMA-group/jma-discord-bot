# JMA Discord Bot

Based on a bot made by Loki and Bertram, rewritten in Python by fancyfinn9

## Testing

1. Clone the repository: `git clone https://github.com/Minetest-JMA-group/jma-discord-bot && cd jma-discord-bot`
2. Install requirements: `pip3 install requirements.txt`
3. Create a Discord bot and create the .env file: `cat .env.example > .env`
4. Populate the .env file with your bot token and Discord IDs: `nano .env`
5. Run the bot: `python3 main.py`

## Features
- Modular system, so most features provided by independent "cogs"
- Humorous error messages
- Proper permission checks

### Core
- Automatic loading of specified cogs
- Error handling and logging
- Reload cogs (command)

### DebugCog
- List all server roles (command)

### DMUserCog
- Send DMs to a user (command)

### EnvEditCog
- Admins and Bot Manager can edit values of .env  (command)

### OneWordStoryCog
- WIP: Add all eligible messages in specified channel to the current story
- Edit the current story (command)

### PingReactCog
- React to a message when pinged
- If pinged with a specific message content, reply with a predetermined message

### PurgeCog
- Purge all messages after a specified one (command) (may move to DebugCog in future)

### ServerStatusCog
- Send custom menu for changing "server status" roles (command)
- Ping roles in specified channel when set to online

### StatusCog
- Change the bot's status, supports all Discord presences (command)

### SuggestionsCog
- Adds thumbs up/down and a discussion thread to all messages in a specified channel
