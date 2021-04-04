from mwenclubhouse_discord.commands.schedule.next_command import UserCommandDone
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.features.calendar import create_firebase_todo_calendar


class UserCommandBreak(UserCommandDone):

    async def insert_break(self, redo_task=True, title='break'):
        top_item, response = await self.get_new_today_task()
        response.insert(0, create_firebase_todo_calendar(title=title))
        if top_item is not None and redo_task:
            response.insert(1,
                            create_firebase_todo_calendar(task_id=top_item['task_id'], title=top_item['title']))
        await self.reformat_calendar(response)
        await self.list_action()

    async def run(self):
        await self.insert_break()


class UserCommandWait(UserCommandBreak):

    async def run(self):
        await self.insert_break(redo_task=False, title='wait')

