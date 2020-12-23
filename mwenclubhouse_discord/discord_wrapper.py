from discord.channel import DMChannel, CategoryChannel, TextChannel


def find_category(channels, category_name):
    for item in channels:
        if type(item) is CategoryChannel and \
                str(item).lower() == category_name:
            return item.channels
    return None


def list_channel(channels, category_name):
    category_name = category_name.lower()
    if category_name == 'personal':
        return 'You do not have access to this channel (unless you are Matthew Wen)'
    category = find_category(channels, category_name)
    if category is not None:
        response = ''
        for text in category:
            if type(text) is TextChannel:
                response += f'`name: {text.name}, id: {text.id}`\n'
        return response if response != '' else '`Channel is Empty`'
    return '`Channel Not Found`'


def list_category(channels):
    response = ''
    for item in channels:
        if type(item) is CategoryChannel and str(item) != 'Personal':
            response += f'{str(item).lower()}\n'
    return f'`{response}`'


class DiscordWrapper:

    def __init__(self, client):
        self.client = client

    async def join_channel(self, channel_id, author):
        channel = self.client.get_channel(int(channel_id))
        if channel is not None:
            await channel.set_permissions(author, read_messages=True, send_messages=True)
            return f'Joining {channel}'
        return 'Channel is Not Found'

    async def handle_dm(self, message):
        if type(message.channel) is not DMChannel:
            return
        content = message.content
        if content.startswith('ls'):
            arg = content[3:]
            category = self.client.get_all_channels()
            response = list_category(category) if arg == '' else list_channel(category, arg)
            await message.channel.send(response)
        elif content.startswith('join'):
            response = await self.join_channel(content[5:], message.author)
            await message.channel.send(response)
