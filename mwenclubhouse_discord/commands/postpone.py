from mwenclubhouse_discord.commands.done import UserCommandDone
from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.features.calendar import create_firebase_todo_calendar


class UserCommandPostpone(UserCommandDone):

    def __init__(self, author, content, response: UserResponse):
        super().__init__(author, content, response)

    async def postpone(self):
        top_item, response = await self.get_new_today_task()
        if top_item is not None:
            response.append(create_firebase_todo_calendar(task_id=top_item['task_id'], title=top_item['title']))
        await self.reformat_calendar(response)
        await self.list_action()

    async def run(self):
        await self.postpone()
