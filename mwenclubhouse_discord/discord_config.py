import discord
import os
from dotenv import load_dotenv

from .commands.ls import UserCommandLS
from .commands.cd import UserCd
from .commands.ppwd import UserPWD
from .commands.leave import UserCommandLeave
from .commands.join import UserCommandJoin
from .common.user_response import UserResponse
from .wrappers.discord_wrapper import DiscordWrapper
from .wrappers.firebase_wrapper import FirebaseWrapper

load_dotenv()
client = discord.Client()
DiscordWrapper.client = client
DiscordWrapper.fire_b = FirebaseWrapper()
discord_wrapper = DiscordWrapper()


def create_command(content):
    commands = [
        ('$ls', UserCommandLS), ('$cd', UserCd), ('$pwd', UserPWD),
        ('$join', UserCommandJoin), ('$leave', UserCommandLeave)
    ]
    for i, (v, t) in enumerate(commands):
        if content.startswith(v):
            return t
    return None


def handle_direct_message(message, response: UserResponse):
    if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id):
        if type(message.channel) is not discord.DMChannel:
            return
    content = message.content.lower()
    obj = create_command(content)
    if obj is None:
        return
    obj(message.author, content, response).run()


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    response: UserResponse = UserResponse()
    handle_direct_message(message, response)
    await response.send_message(message)


def run_discord():
    client.run(os.getenv('TOKEN'))
