from mwenclubhouse_discord.commands.command_break import UserCommandBreak
from mwenclubhouse_discord.common import UserResponse


class UserCommandWait(UserCommandBreak):

    def __init__(self, author, content, response: UserResponse):
        super().__init__(author, content, response)

    async def run(self):
        await self.insert_break(redo_task=False, title='wait')
