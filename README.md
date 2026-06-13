# JMA Discord Bot

<a href="https://codeberg.org/Minetest-JMA-group/jma-discord-bot" target="_blank"><img alt="codeberg" height="45" src="https://cdn.jsdelivr.net/npm/@intergrav/devins-badges@3/assets/cozy/available/codeberg_vector.svg"></a> <a href="https://discord.gg/zsRZWmwnVS" target="_blank"><img alt="discord-plural" height="45" src="https://cdn.jsdelivr.net/npm/@intergrav/devins-badges@3/assets/cozy/social/discord-plural_vector.svg"></a>

Utility bot for JMA-Gaming-Server on Discord

Based on a bot made by Loki and Bertram, rewritten in Python by fancyfinn9

## Testing

1. Clone the repository: `git clone https://codeberg.org/Minetest-JMA-group/jma-discord-bot.git && cd jma-discord-bot`
2. Install requirements: `pip3 install requirements.txt`
3. Create a Discord bot and create the .env file: `cat .env.example > .env`
4. Populate the .env file with your bot token and Discord IDs: `nano .env`
5. Run the bot: `python3 main.py`

## Features
- Modular system, so most features provided by independent "cogs"
- Humorous error messages
- Proper permission checks

## License

Copyright (C) 2026 fancyfinn9 <fancyfinn9@proton.me>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.