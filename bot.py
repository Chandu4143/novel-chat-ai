# bot.py

import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

async def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get tokens and settings from environment variables
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    
    if not bot_token:
        print("ERROR: DISCORD_BOT_TOKEN not found in .env file.")
        return

    # Define the bot's intents
    # We need message_content to read messages and DMs.
    intents = discord.Intents.default()
    intents.message_content = True
    intents.dm_messages = True

    # Create the bot instance
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
        print('Bot is ready to analyze documents in DMs.')
        print('------')

    # Load the document cog
    await bot.load_extension("cogs.document_cog")
    
    # Run the bot
    await bot.start(bot_token)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is shutting down.")