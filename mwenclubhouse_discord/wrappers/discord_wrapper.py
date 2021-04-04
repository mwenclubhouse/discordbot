from typing import List

import discord

from .calendar_wrapper import CalendarWrapper
from .firebase_wrapper import FirebaseWrapper


class DiscordWrapper:
    client = None
    fire_b: FirebaseWrapper = None
    gCal: CalendarWrapper = None

    @staticmethod
    async def get_channel(channel_id):
        return DiscordWrapper.client.get_channel(channel_id)

    @staticmethod
    async def clear_channel(channel_id):
        channel: discord.channel.TextChannel = await DiscordWrapper.get_channel(channel_id)
        messages: List[discord.message.Message] = await channel.history(oldest_first=True, limit=50).flatten()
        for i in messages:
            await i.delete()

    @staticmethod
    async def get_message(channel_id, message_id):
        channel = await DiscordWrapper.get_channel(channel_id)
        if channel is not None:
            return await channel.fetch_message(message_id)
        return None
