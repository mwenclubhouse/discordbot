from datetime import datetime
from typing import List

from mwenclubhouse_discord.commands.sch import UserCommandSch
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.features.calendar import time_in_event
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommandDone(UserCommandSch):

    def __init__(self, author, content, response: UserResponse):
        super().__init__(author, content, response)

    async def mark_done(self):
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        if len(response) == 0:
            self.response.set_error_response(0, True)
            return

        i = 0
        top_item = response[0]
        for i, item in enumerate(response[1:]):
            if (top_item['task_id'] != item['task_id'] or
                    top_item['title'] != item['title']):
                break
        i += 1

        self.gcal.complete_calendar(response[:i])
        response = response[i:]

        epoch_time = DiscordWrapper.fire_b.get_user_end_time(self.author.id)
        if epoch_time is None:
            self.response.set_error_response(0, True)
            return

        end_time = datetime.fromtimestamp(epoch_time)
        self.adjust_calendar(response, end_time=end_time)
        await self.list_action()

    async def sch_run(self):
        await self.mark_done()
