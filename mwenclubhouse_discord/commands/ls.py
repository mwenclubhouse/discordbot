from mwenclubhouse_discord.commands.command import UserCommand
from mwenclubhouse_discord.common import list_categories, get_channel_type
import discord
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


def parse_channels(category):
    discord_response = discord.Embed()
    if category is not None:
        for i, text in enumerate(category):
            discord_response.add_field(name=f'{i}: {text.name}', value=f'{get_channel_type(text)}', inline=False)
        return discord_response

    discord_response.add_field(name='Error', value='Channel is Not Found')
    return discord_response


class UserCommandLS(UserCommand):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)
        self.category = None
        self.raw_category = None

    def set_raw_simple_category(self, category):
        self.raw_category = category
        self.category = [i.id for i in category]

    def set_category_by_location(self, location):
        if location == '':
            query = DiscordWrapper.client.get_all_channels()
            category = list_categories(query)
        else:
            query = DiscordWrapper.client.get_channel(location)
            category = query.channels if query is not None else []
        self.set_raw_simple_category(category)

    def get_response(self):
        if self.category is None:
            location = DiscordWrapper.fire_b.get_property('location', self.author.id)
            self.set_category_by_location(location)
        DiscordWrapper.fire_b.upload_selection('ls', self.author.id, self.category)
        return parse_channels(self.raw_category)

    async def run(self):
        if not self.response.done:
            self.response.add_response(self.get_response(), done=True)
