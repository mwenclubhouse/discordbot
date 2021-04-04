from mwenclubhouse_discord.commands import UserCommand
from mwenclubhouse_discord.common.utils import *
from mwenclubhouse_discord.common.error import UserError
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


def parse_channels(category):
    discord_response = discord.Embed()
    if category is not None:
        for i, text in enumerate(category):
            discord_response.add_field(name=f'{i}: {text.name}', value=f'{get_channel_type(text)}', inline=False)
        return discord_response

    discord_response.add_field(name='Error', value='Channel is Not Found')
    return discord_response


class UserPWD(UserCommand):

    @property
    def location_name(self):
        location = DiscordWrapper.fire_b.get_property('location', self.author.id)
        if location != '':
            channel = DiscordWrapper.client.get_channel(location)
            location = '' if channel is None else ("" + channel.name)
        return "root" if location == '' else location

    async def run(self):
        location = self.location_name
        response = create_simple_message('location', f'{location.lower()}')
        self.response.set_success_response(response)


class UserCommandLS(UserCommand):

    def __init__(self, message, response):
        super().__init__(message, response)
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


class UserCd(UserCommandLS):

    def __init__(self, message, response, idx=None):
        super().__init__(message, response)
        self.idx = self.content[4:] if idx is None else idx

    def handle_no_idx(self):
        back_to_root = self.idx in ['', '..']
        if back_to_root:
            DiscordWrapper.fire_b.clear_selected('ls', self.author.id)
            DiscordWrapper.fire_b.set_property('location', self.author.id, '')
        if self.idx == '.' or back_to_root:
            self.response.set_success_response(super().get_response())

    def handle_parse_input(self):
        super().parse_input_set_head('ls', UserError.PS_ENTER_NUM, UserError.UE_ENTER_LS)

    def handle_category(self):
        if self.head is None:
            self.response.set_error_response(UserError.CE_TYPE_LS_A)
        elif type(self.head) is not CategoryChannel:
            self.response.set_error_response(UserError.UE_CD)

    def handle_new_location(self):
        DiscordWrapper.fire_b.set_property('location', self.author.id, self.head.id)
        self.set_raw_simple_category(self.head.channels)
        self.response.set_success_response(super().get_response())

    async def run(self):
        if not self.response.done:
            steps = [self.handle_no_idx, self.handle_parse_input,
                     self.handle_category, self.handle_new_location]
            for i in steps:
                i()
                if self.response.done:
                    return
