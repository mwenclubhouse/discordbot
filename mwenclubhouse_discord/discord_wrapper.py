import discord
from discord.channel import DMChannel, CategoryChannel, TextChannel, VoiceChannel
from discord import Permissions
from .firebase_wrapper import FirebaseWrapper


def find_category(channels, category_name):
    for item in channels:
        if type(item) is CategoryChannel and \
                str(item).lower() == category_name:
            return item.channels
    return None


def list_categories(channels):
    response = []
    for item in channels:
        if type(item) is CategoryChannel and str(item) != 'Personal':
            response.append(item)
    return response


def get_channel_type(channel):
    if type(channel) is TextChannel:
        return "Text Channel"
    if type(channel) is VoiceChannel:
        return "Voice Channel"
    if type(channel) is CategoryChannel:
        return "Category Channel"


def create_simple_message(name, value):
    return discord.Embed().add_field(name=name, value=value, inline=False)


def parse_channels(category):
    response = discord.Embed()
    if category is not None:
        for i, text in enumerate(category):
            response.add_field(name=f'{i}: {text.name}', value=f'{get_channel_type(text)}', inline=False)
        return response

    response.add_field(name='Error', value='Channel is Not Found')
    return response


def parse_int(s):
    try:
        return int(s)
    except ValueError:
        return None


class DiscordWrapper:

    def __init__(self, client, firebase_wrapper: FirebaseWrapper):
        self.client = client
        self.firebase_wrapper = firebase_wrapper

    def parse_channel(self, channel_id, author):
        selected_channel_id = parse_int(channel_id)
        if selected_channel_id is None:
            return None, "❌", create_simple_message('User Error', 'Invalid Channel ID. Please Input a Number')

        # Join Channel
        channel_id = self.firebase_wrapper.select_by_idx(author.id, selected_channel_id)
        if channel_id is None:
            return None, "❌", create_simple_message('Computer Error', 'Type `ls` to list channel in current category')
        return self.client.get_channel(channel_id), None, None

    async def join_channel(self, channel_id, author):
        channel, emoji, error = self.parse_channel(channel_id, author)
        if error:
            return emoji, error

        if channel is not None:
            await channel.set_permissions(author, read_messages=True, send_messages=True)
            self.firebase_wrapper.set_channel(author.id, channel.id, status=True)
            return "✅", create_simple_message('Success!', f'joining {channel}')

        return "❌", create_simple_message('Computer Error', 'Channel is Not Found')

    async def leave_channel(self, channel_id, author):
        channel, emoji, error = self.parse_channel(channel_id, author)
        if error:
            return emoji, error

        if channel is not None:
            await channel.set_permissions(author, read_messages=False, send_messages=False)
            self.firebase_wrapper.set_channel(author.id, channel.id, status=False)
            return "✅", create_simple_message('Success!', f'leaving {channel}')

        return "❌", create_simple_message('Computer Error', 'Channel is Not Found')

    def handle_cd(self, author, idx):
        # Shortcuts for changing directory
        if idx == '' or idx == '..':
            self.firebase_wrapper.clear_selected(author.id)
            self.firebase_wrapper.set_location(author.id, '')
            return "✅", self.handle_ls(author)
        elif idx == '.':
            return "✅", self.handle_ls(author)

        # Parsing Command
        idx = parse_int(idx)
        if idx is None:
            return "❌", create_simple_message("Parsing Error",
                                              "Please type a number representing a Category Channel you want to enter")
        discord_category = self.firebase_wrapper.select_by_idx(author.id, idx)
        if discord_category is None:
            return "❌", create_simple_message("User Error", "Please type "
                                                            "`ls` to list possible Categories")
        category = self.client.get_channel(discord_category)
        if category is None:
            return "❌", create_simple_message("Computer Error", "Please "
                                                                "type `ls` again.")
        if type(category) is not CategoryChannel:
            return "❌", create_simple_message("User Error", "You cannot"
                                                            " `cd` inside a non Category Channel")
        self.firebase_wrapper.set_location(author.id, category.id)

        # Send Response
        return "✅", self.handle_ls(author, category=category.channels)

    def handle_ls(self, author, category=None):
        if category is None:
            location = self.firebase_wrapper.get_location(author.id)
            if location == '':
                query = self.client.get_all_channels()
                category = list_categories(query)
            else:
                query = self.client.get_channel(location)
                category = query.channels if query is not None else []
        self.firebase_wrapper.upload_ls(author.id, category)
        return parse_channels(category)

    async def handle_pwd(self, author_id):
        location = self.firebase_wrapper.get_location(author_id)
        if location != '':
            channel = self.client.get_channel(location)
            location = '' if channel is None else ("/" + channel.name)
        return create_simple_message('location', f'`mwenclubhouse{location.lower()}`')

    async def handle_dm(self, message):
        if type(message.channel) is not DMChannel and \
                self.firebase_wrapper.is_bot_channel(message.channel.id):
            return
        content = message.content.lower()

        # Handle LS Command
        if content.startswith('$ls'):
            response = self.handle_ls(message.author)
            await message.channel.send(embed=response)

        # Handle cd Command
        elif content.startswith('$cd'):
            emoji, response = self.handle_cd(message.author, content[4:])
            await message.add_reaction(emoji)
            await message.channel.send(embed=response)

        # Handle open Command
        elif content.startswith('$join'):
            emoji, response = await self.join_channel(content[6:], message.author)
            await message.add_reaction(emoji)
            await message.channel.send(embed=response)

        # Handle close Command
        elif content.startswith('$leave'):
            emoji, response = await self.leave_channel(content[7:], message.author)
            await message.add_reaction(emoji)
            await message.channel.send(embed=response)

        # Handle pwd command
        elif content.startswith('$pwd'):
            response = await self.handle_pwd(message.author.id)
            await message.channel.send(embed=response)
