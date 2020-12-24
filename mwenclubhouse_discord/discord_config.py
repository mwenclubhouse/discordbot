import discord
import os
from .discord_wrapper import DiscordWrapper
from .firebase_wrapper import FirebaseWrapper
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()
firebase_wrapper = FirebaseWrapper()
discord_wrapper = DiscordWrapper(client, firebase_wrapper)


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await discord_wrapper.handle_dm(message)


def run_discord():
    client.run(os.getenv('TOKEN'))

