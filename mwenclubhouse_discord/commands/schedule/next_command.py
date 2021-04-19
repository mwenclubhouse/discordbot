from datetime import datetime
from typing import List

from mwenclubhouse_discord.commands.schedule.sch_command import UserCommandSch
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.features.calendar import create_firebase_todo_calendar
from mwenclubhouse_discord.features.todoist import MWTodoist
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class LocalUser:

    def __init__(self, user_id):
        self.id = user_id


class UserCommandDone(UserCommandSch):

    def __init__(self, message, response: UserResponse, payload):
        self.payload = payload
        response.edit_message = True
        response.remove_emoji = [(payload.emoji.name, payload.member)]
        super().__init__(message, response)
        self.todo = MWTodoist()

    @property
    def author(self):
        return LocalUser(self.payload.user_id)

    async def get_new_today_task(self):
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        if len(response) == 0:
            self.response.set_error_response(0, True)
            return None, []

        i = 0
        top_item = response[0]
        delete_event = top_item['title'] in ['wait', 'break']

        found_end = False
        for i, item in enumerate(response):
            if (top_item['task_id'] != item['task_id'] or
                    top_item['title'] != item['title']):
                found_end = True
                break
            elif delete_event:
                self.gcal.delete_calendar(item)

        if not found_end:
            i = len(response)

        if not delete_event:
            self.gcal.complete_calendar(response[:i], self.todo)
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


class UserCommandPostpone(UserCommandDone):

    async def postpone(self):
        top_item, response = await self.get_new_today_task()
        if top_item is not None:
            response.append(create_firebase_todo_calendar(task_id=top_item['task_id'], title=top_item['title']))
        await self.reformat_calendar(response)
        await self.list_action()

    async def run(self):
        await self.postpone()
