from datetime import datetime, timedelta

import discord
import pytz
from discord.channel import CategoryChannel, TextChannel, VoiceChannel
from .error import all_error_types
from mwenclubhouse_discord.features.todoist import get_parsed_date, get_task_url


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


def parse_int(s):
    try:
        return int(s)
    except ValueError:
        return None


def iterate_commands(content, commands, starts_with=True):
    for v, t in commands:
        if (starts_with and content.startswith(v)) or \
                (not starts_with and content == v):
            return t
    return None


def iterate_emojis(emoji, commands):
    for v, t in commands:
        if v == emoji:
            return t
    return None


def add_todoist_field(message, i, t, todo):
    project = todo.get_project(t['project_id'])
    due_date = get_parsed_date(t, parentheses=True, timezone=todo.get_timezone())
    parent = todo.get_parent_task(None, item=t)
    url = get_task_url(parent['id'])
    message.add_field(name=f'{i}: {due_date} {project["project"]["name"]}',
                      value=f'[{parent["content"]}]({url})',
                      inline=False)


def create_message_todoist(options, todo, priority=None):
    message = None
    added_field = 0
    for i, task in enumerate(options):
        if priority is None or priority == task['priority']:
            message = discord.Embed() if message is None else message
            added_field += 1
            add_todoist_field(message, i, task, todo)
    if message is not None:
        if priority is not None:
            message.title = f"Priority {priority} task{'s' if added_field > 1 else ''}"
        else:
            message.title = 'All Todoist Tasks'
    return message


def create_message_todoist_and_title(options, todo):
    message = discord.Embed()
    if len(options) > 0:
        for i, task in enumerate(options):
            if task['type'] == 'todoist':
                add_todoist_field(message, i, task['item'], todo)
            elif task['type'] == 'custom':
                c = task['item']
                message.add_field(name=f'{i}: {c}',
                                  value='Custom Task',
                                  inline=False)
    else:
        message.add_field(name="List is Empty", value="Add Tasks To Schedule")
    return message


def swap_items(items, idx1, idx2, error=None):
    if idx1 < len(items) and idx2 < len(items):
        temp = items[idx1]
        items[idx1] = items[idx2]
        items[idx2] = temp
    elif error:
        error()


def get_datetime_from_hour_minute(hour, minute, user_timezone):
    d = datetime.now(pytz.timezone(user_timezone))
    d = d.replace(hour=hour, minute=minute)
    if d.timestamp() < datetime.now().timestamp():
        d = d + timedelta(days=1)
    return d
