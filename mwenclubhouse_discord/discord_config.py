import discord
import os
from .discord_wrapper import DiscordWrapper
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()
wrapper = DiscordWrapper(client)


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await wrapper.handle_dm(message)


def run_discord():
    client.run(os.getenv('TOKEN'))

