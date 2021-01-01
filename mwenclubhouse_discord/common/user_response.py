import discord
from discord import CategoryChannel

from mwenclubhouse_discord.common import get_error_response
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserResponse:

    def __init__(self, done=False):
        self.response = []
        self.done = done
        self.emoji = []

        # (Channel, Author, Access)
        self.permissions = []
        self.loading = False

    @property
    def response_tail(self):
        if len(self.response) == 0:
            return None
        return self.response[-1]

    def set_error_response(self, idx, done=True):
        if not self.done:
            error = get_error_response(idx, self.response_tail)
            self.add_response(error)
            self.set_state(False, done)

    def set_success_response(self, response, done=True):
        if not self.done:
            self.add_response(response)
            self.set_state(True, done)

    def set_state(self, state, done=False):
        if not self.done:
            state_emoji = "✅" if state else "❌"
            self.emoji.append(state_emoji)
            self.done = self.done or done

    def add_response(self, item, done=False):
        if not self.done:
            self.done = self.done or done
            if item is not None and item != self.response_tail:
                self.response.append(item)

    def add_permissions(self, author, channel, access):
        if not self.done:
            DiscordWrapper.fire_b.set_channel(author.id, channel.id, status=True)
            self.permissions.append((author, channel, access))
            if type(channel) is CategoryChannel:
                for i in channel.channels:
                    self.add_permissions(author, i, access)

    async def send_loading(self, message):
        if self.loading:
            response = discord.Embed().add_field(name="Loading", value="Loading Content")
            await message.channel.send(embed=response)

    async def send_message(self, message):
        for author, channel, access in self.permissions:
            await channel.set_permissions(author, read_messages=access, send_messages=access)
        for i in self.emoji:
            await message.add_reaction(i)
        for i in self.response:
            if type(i) is str:
                await message.channel.send(i)
            else:
                await message.channel.send(embed=i)
