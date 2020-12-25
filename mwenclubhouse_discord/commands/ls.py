from mwenclubhouse_discord.commands.command import UserCommand
from mwenclubhouse_discord.common import list_categories, parse_channels
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommandLS(UserCommand):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)
        self.category = None

    def set_category_by_location(self, location):
        if location == '':
            query = DiscordWrapper.client.get_all_channels()
            self.category = list_categories(query)
        else:
            query = DiscordWrapper.client.get_channel(location)
            self.category = query.channels if query is not None else []

    def get_response(self):
        if self.category is None:
            location = DiscordWrapper.fire_b.get_location(self.author.id)
            self.set_category_by_location(location)
        DiscordWrapper.fire_b.upload_ls(self.author.id, self.category)
        return parse_channels(self.category)

    def run(self):
        if not self.response.done:
            self.response.add_response(self.get_response(), done=True)
