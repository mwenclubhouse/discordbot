from datetime import datetime
from typing import List

from mwenclubhouse_discord.commands.sch import UserCommandSch
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommandDone(UserCommandSch):

    def __init__(self, author, content, response: UserResponse):
        super().__init__(author, content, response)

    async def mark_done(self):
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        if len(response) == 0:
            self.response.set_error_response(0, True)
            return

        working_item = response[0]
        if working_item['cal_id'] is None:
            self.response.set_error_response(0, True)
            return

        self.gcal.complete_calendar(working_item)
        response = response[1:]

        epoch_time = DiscordWrapper.fire_b.get_user_end_time(self.author.id)
        if epoch_time is None:
            self.response.set_error_response(0, True)
            return

        end_time = datetime.fromtimestamp(epoch_time)
        self.adjust_calendar(response, end_time)

    async def run(self):
        await self.mark_done()
