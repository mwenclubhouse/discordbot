from mwenclubhouse_discord.common import parse_int
from mwenclubhouse_discord.common.user_response import UserResponse
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommand:

    def __init__(self, author, content, response: UserResponse):
        self.author = author
        self.content = content
        self.response = response
        self.head = None
        self.idx = 0

    def parse_input(self, idx_none=0, category_none=0):
        idx = parse_int(self.idx)
        if idx is None:
            self.response.set_error_response(idx_none)
            return

        discord_category = DiscordWrapper.fire_b.select_by_idx(self.author.id, idx)
        if discord_category is None:
            self.response.set_error_response(category_none)
            return
        self.head = DiscordWrapper.client.get_channel(discord_category)

    def run(self):
        pass
