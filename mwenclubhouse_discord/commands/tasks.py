from .ls import UserCommandLS
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper
from mwenclubhouse_discord.common.utils import create_message_todoist, create_simple_message
from mwenclubhouse_discord.features.todoist import MWTodoist


class UserCommandTasks(UserCommandLS):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)
        response.loading = True
        self.todo = MWTodoist()

    def set_raw_simple_category(self, category):
        self.raw_category = category
        self.category = [i['id'] for i in category]

    def set_response(self):
        if self.category is None:
            self.set_raw_simple_category(self.todo.get_upcoming_tasks())
        DiscordWrapper.fire_b.upload_selection('ls-tasks', self.author.id, self.category)

        added_response = 0
        for i in [4, 3, 2, 1]:
            response = create_message_todoist(self.raw_category, self.todo, priority=i)
            if response is not None:
                added_response += 1
                self.response.add_response(response)
        if added_response == 0:
            message = create_simple_message('No Tasks in Todoists', 'Add Tasks in Todoists to display them on discord')
            self.response.add_response(message)
        self.response.done = True

    async def run(self):
        self.set_response()
