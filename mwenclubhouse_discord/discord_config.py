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
from .common.utils import iterate_commands, iterate_emojis

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


def create_scheduler_message_command(content):
    return iterate_commands(content, [
        ('$tasks', UserCommandTasks),
        ('$sch', UserCommandSch), ('$gauth', GAuthCommand),

    ])


def create_scheduler_emoji_command(emoji):
    return iterate_emojis(emoji, [
        ('✅', UserCommandDone), ('⏭', UserCommandDone), ('🥛', UserCommandBreak),
        ('⌛', UserCommandWait), ('🔀', UserCommandPostpone)
    ])


async def run(obj, message, response, payload=None):
    if obj is not None:
        if payload is None:
            inst: UserCommand = obj(message, response)
        else:
            inst: UserCommand = obj(message, response, payload)

        await response.send_loading(message)
        await inst.run()


def is_correct_channel(message, channel_name):
    if not DiscordWrapper.fire_b.is_bot_channel(message.channel.id, channel_name):
        if type(message.channel) is not discord.DMChannel:
            return False
    return True


async def handle_direct_message(message, response: UserResponse):
    if is_correct_channel(message, 'bot-command'):
        content = message.content.lower()
        await run(create_direct_command(content), message, response)


async def handle_scheduler_message(message, response: UserResponse):
    if is_correct_channel(message, 'bot-schedule'):
        obj = create_scheduler_message_command(message.content)
        await run(obj, message, response)


async def handle_schedule_emoji(message, emoji, response: UserResponse, payload):
    """
    done: ✅
    next: ⏭️
    wait: ⌛
    break: 🥛
    postpone: 🔀
    """
    if is_correct_channel(message, 'bot-schedule'):
        obj = create_scheduler_emoji_command(emoji)
        await run(obj, message, response, payload=payload)


@client.event
async def on_ready():
    pass


@client.event
async def on_raw_reaction_add(payload: discord.raw_models.RawReactionActionEvent):
    if payload.user_id == client.user.id:
        return
    response: UserResponse = UserResponse()
    message: discord.message.Message = await DiscordWrapper.get_message(payload.channel_id, payload.message_id)
    list_type = [handle_schedule_emoji]

    for i in list_type:
        await i(message, payload.emoji.name, response, payload)
        if response.done:
            await response.send_message(message)


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
