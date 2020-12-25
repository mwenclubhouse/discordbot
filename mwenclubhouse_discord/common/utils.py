import discord
from discord.channel import CategoryChannel, TextChannel, VoiceChannel
from .error import all_error_types


def find_category(channels, category_name):
    for item in channels:
        if type(item) is CategoryChannel and \
                str(item).lower() == category_name:
            return item.channels
    return None


def list_categories(channels):
    categories = []
    for item in channels:
        if type(item) is CategoryChannel and str(item) != 'Personal':
            categories.append(item)
    return categories


def get_channel_type(channel):
    if type(channel) is TextChannel:
        return "Text Channel"
    if type(channel) is VoiceChannel:
        return "Voice Channel"
    if type(channel) is CategoryChannel:
        return "Category Channel"


def create_simple_message(name, value, embed=None):
    if type(embed) != discord.Embed:
        embed = discord.Embed()
    return embed.add_field(name=name, value=value, inline=False)


def get_error_response(idx, embed=None):
    if idx >= len(all_error_types):
        return None
    item = all_error_types[idx]
    return create_simple_message(item['title'], item['msg'], embed)


def parse_channels(category):
    discord_response = discord.Embed()
    if category is not None:
        for i, text in enumerate(category):
            discord_response.add_field(name=f'{i}: {text.name}', value=f'{get_channel_type(text)}', inline=False)
        return discord_response

    discord_response.add_field(name='Error', value='Channel is Not Found')
    return discord_response


def parse_int(s):
    try:
        return int(s)
    except ValueError:
        return None
