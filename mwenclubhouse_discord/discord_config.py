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


def iterate_commands(content, commands):
    for v, t in commands:
        if content.startswith(v):
            return t
    return None


def create_direct_command(content):
    return iterate_commands(content, [
        ('$ls', UserCommandLS), ('$cd', UserCd), ('$pwd', UserPWD),
        ('$join', UserCommandJoin), ('$leave', UserCommandLeave)
    ])


def create_scheduler_command(content):
    return iterate_commands(content, [])


def run(obj, author, content, response):
    if obj is not None:
        obj(author, content, response).run()


def handle_direct_message(message, response: UserResponse):
    if not response.done:
        if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id, 'bot-command'):
            if type(message.channel) is not discord.DMChannel:
                return
        content = message.content.lower()
        run(create_direct_command(content), message.author, content, response)


def handle_scheduler_message(message, response: UserResponse):
    if not response.done:
        if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id, 'bot-schedule'):
            return
        obj = create_scheduler_command(message.content)
        run(obj, message.author, message.content, response)


@client.event
async def on_ready():
    pass


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    response: UserResponse = UserResponse()
    list_type = [handle_direct_message, handle_scheduler_message]
    for i in list_type:
        i(message, response)
        if response.done:
            await response.send_message(message)
            return


def run_discord():
    client.run(os.getenv('TOKEN'))
