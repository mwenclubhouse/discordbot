from .ls import UserCommandLS
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper
from mwenclubhouse_discord.common.utils import create_message_todoist
from mwenclubhouse_discord.features.todoist import MWTodoist


class UserCommandTasks(UserCommandLS):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)
        response.loading = True
        self.todo = MWTodoist()

    def set_raw_simple_category(self, category):
        self.raw_category = category
        self.category = [i['id'] for i in category]

    def get_response(self):
        if self.category is None:
            self.set_raw_simple_category(self.todo.get_upcoming_tasks())
        DiscordWrapper.fire_b.upload_selection('ls-tasks', self.author.id, self.category)
        return create_message_todoist(self.raw_category, self.todo)

    async def run(self):
        await super().run()
