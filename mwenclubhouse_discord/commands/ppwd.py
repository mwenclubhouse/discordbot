from mwenclubhouse_discord.commands.command import UserCommand
from mwenclubhouse_discord.common import create_simple_message
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserPWD(UserCommand):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)

    @property
    def location_name(self):
        location = DiscordWrapper.fire_b.get_property('location', self.author.id)
        if location != '':
            channel = DiscordWrapper.client.get_channel(location)
            location = '' if channel is None else ("" + channel.name)
        return "root" if location == '' else location

    def run(self):
        location = self.location_name
        response = create_simple_message('location', f'{location.lower()}')
        self.response.set_success_response(response)
