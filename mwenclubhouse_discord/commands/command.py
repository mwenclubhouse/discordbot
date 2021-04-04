import discord

from mwenclubhouse_discord.common import parse_int
from mwenclubhouse_discord.common.user_response import UserResponse
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommand:

    def __init__(self, message: discord.message.Message, response: UserResponse):
        self.message = message
        self.response = response
        self.head = None
        self.idx = 0

    @property
    def author(self):
        return self.message.author

    @property
    def content(self):
        return self.message.content

    def parse_input_get_item(self, key, idx_none=0, category_none=0):
        idx = parse_int(self.idx)
        if idx is None:
            self.response.set_error_response(idx_none)
            return None

        discord_category = DiscordWrapper.fire_b.select_by_idx(key, self.author.id, idx)
        if discord_category is None:
            self.response.set_error_response(category_none)
            return None
        return discord_category

    def parse_input_set_head(self, key, idx_none=0, category_none=0):
        response = self.parse_input_get_item(key, idx_none, category_none)
        if response:
            self.head = DiscordWrapper.client.get_channel(response)

    async def run(self):
        pass
