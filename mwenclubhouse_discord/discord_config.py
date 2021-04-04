import discord
import os
if os.getenv("PRODUCTION", None) != "1":
    from dotenv import load_dotenv

    load_dotenv()

from .commands import UserCommand
from mwenclubhouse_discord.commands.schedule.next_command import UserCommandDone
from mwenclubhouse_discord.commands.schedule.gauth_command import GAuthCommand
from mwenclubhouse_discord.commands.groupme.info_commands import UserCommandLS
from mwenclubhouse_discord.commands.groupme.info_commands import UserCd, UserPWD
from mwenclubhouse_discord.commands.schedule.next_command import UserCommandPostpone
from mwenclubhouse_discord.commands.schedule.tasks_command import UserCommandTasks
from mwenclubhouse_discord.commands.groupme.action_commands import UserCommandLeave
from mwenclubhouse_discord.commands.groupme.action_commands import UserCommandJoin
from mwenclubhouse_discord.commands.schedule.sch_command import UserCommandSch
from mwenclubhouse_discord.commands.schedule.break_command import UserCommandBreak
from mwenclubhouse_discord.commands.schedule.break_command import UserCommandWait
from .common.user_response import UserResponse
from .wrappers.calendar_wrapper import CalendarWrapper
from .wrappers.discord_wrapper import DiscordWrapper
from .wrappers.firebase_wrapper import FirebaseWrapper
from .common.utils import iterate_commands

client = discord.Client()
DiscordWrapper.client = client
DiscordWrapper.fire_b = FirebaseWrapper()
DiscordWrapper.gCal = CalendarWrapper()
discord_wrapper = DiscordWrapper()


def create_direct_command(content):
    return iterate_commands(content, [
        ('$ls', UserCommandLS), ('$cd', UserCd), ('$pwd', UserPWD),
        ('$join', UserCommandJoin), ('$leave', UserCommandLeave)
    ])


def create_scheduler_command(content):
    return iterate_commands(content, [
        ('$tasks', UserCommandTasks),
        ('$sch', UserCommandSch), ('$gauth', GAuthCommand),
        ('$done', UserCommandDone), ('$break', UserCommandBreak),
        ('$wait', UserCommandWait), ('$postpone', UserCommandPostpone)
    ])


async def run(obj, message, response):
    if obj is not None:
        inst: UserCommand = obj(message, response)
        await response.send_loading(message)
        await inst.run()


async def handle_direct_message(message, response: UserResponse):
    if not response.done:
        if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id, 'bot-command'):
            if type(message.channel) is not discord.DMChannel:
                return
        content = message.content.lower()
        await run(create_direct_command(content), message, response)


async def handle_scheduler_message(message, response: UserResponse):
    if not response.done:
        if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id, 'bot-schedule'):
            return
        obj = create_scheduler_command(message.content)
        await run(obj, message, response)


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
        await i(message, response)
        if response.done:
            await response.send_message(message)
            return


def run_discord():
    client.run(os.getenv('TOKEN'))
