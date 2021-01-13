from datetime import datetime
from typing import List

from mwenclubhouse_discord.commands.sch import UserCommandSch
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCommandDone(UserCommandSch):

    def __init__(self, author, content, response: UserResponse):
        super().__init__(author, content, response)

    async def get_new_today_task(self):
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        if len(response) == 0:
            self.response.set_error_response(0, True)
            return None, []

        i = 0
        top_item = response[0]
        delete_event = top_item['title'] == 'wait'
        for i, item in enumerate(response):
            if (top_item['task_id'] != item['task_id'] or
                    top_item['title'] != item['title']):
                break
            elif delete_event:
                self.gcal.delete_calendar(item)

        if not delete_event:
            self.gcal.complete_calendar(response[:i])
        return top_item, response[i:]

    async def reformat_calendar(self, response):
        epoch_time = DiscordWrapper.fire_b.get_user_end_time(self.author.id)
        if epoch_time is None:
            self.response.set_error_response(0, True)
            return

        end_time = datetime.fromtimestamp(epoch_time)
        self.adjust_calendar(response, end_time=end_time)

    async def mark_done(self):
        _, response = await self.get_new_today_task()
        await self.reformat_calendar(response)
        await self.list_action()

    async def sch_run(self):
        await self.mark_done()
