from typing import List, Dict

from mwenclubhouse_discord.common import UserResponse
from mwenclubhouse_discord.common.utils import *
from mwenclubhouse_discord.features.calendar import MWCalendar, create_firebase_todo_calendar
from mwenclubhouse_discord.features.todoist import MWTodoist
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper
from . import UserCommand
from mwenclubhouse_discord.common.error import UserError


class UserCommandSch(UserCommand):

    def __init__(self, author, content: str, response: UserResponse):
        super().__init__(author, content, response)
        self.args = None
        self.parse_arguments(content)
        self.tasks = []
        self.raw_tasks = []
        self.todo: MWTodoist = MWTodoist()
        self.gcal: MWCalendar = MWCalendar(author.id)

    def parse_arguments(self, content):
        args = content[5:]
        args.lower()
        self.args = args.split()

    def set_raw_simple_tasks(self, tasks_by_id):
        self.tasks = tasks_by_id
        self.raw_tasks = [
            {'type': 'todoist', 'item': self.todo.get_item(i['task_id'])}
            if i['task_id'] else {'type': 'custom', 'item': i['title']}
            for i in tasks_by_id]

    def get_two_arguments(self, idx2_can_be_string=False):
        if len(self.args[1:]) < 2:
            self.response.set_error_response(0, True)
            return None, None
        idx1, idx2 = parse_int(self.args[1]), parse_int(self.args[2])
        if idx1 is None:
            self.response.set_error_response(0, True)
            return None, None
        elif idx2 is None:
            if not idx2_can_be_string:
                self.response.set_error_response(0, True)
                return None, None
            else:
                idx2 = self.args[2]
        return idx1, idx2

    def parse_time_arguments(self):
        if len(self.args) == 0:
            return 0, None, None

        arguments = "".join(self.args[1:])
        time, am_pm = arguments[:-2], arguments[-2:]
        if am_pm not in ['am', 'pm']:
            return 0, None, None

        if ':' in time:
            hour, minute = time.split(':')
            hour, minute = parse_int(hour), parse_int(minute)
        else:
            hour, minute = parse_int(time), 0

        if None in [hour, minute]:
            return 0, None, None
        if hour == 12:
            return (None, 0, minute,) if am_pm == 'am' else (None, 12, minute,)
        if am_pm == 'pm':
            hour += 12
        return None, hour, minute

    async def add_action(self):
        selection_options: List = DiscordWrapper.fire_b.get_property('ls-tasks', self.author.id, [])
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        for i in self.args[1:]:
            idx = parse_int(i)
            if idx is not None and idx < len(selection_options):
                item = create_firebase_todo_calendar(task_id=selection_options[idx])
            else:
                item = create_firebase_todo_calendar(title=i)
            response.append(item)
        DiscordWrapper.fire_b.set_property('today-task', self.author.id, response)
        await self.list_action()

    def is_valid_index(self, idx, items):
        if idx >= len(items):
            self.response.set_error_response(0, True)

    def getting_options_and_parameters(self):
        idx1, idx2 = self.get_two_arguments(idx2_can_be_string=True)
        if self.response.done:
            return
        # Users Schedule
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        self.is_valid_index(idx1, response)

        # Options To Add
        selection_options = []
        if type(idx2) is int:
            selection_options: List = DiscordWrapper.fire_b.get_property('ls-tasks', self.author.id, [])
            self.is_valid_index(idx2, selection_options)

        return idx1, response, idx2, selection_options

    async def insert_action(self):
        idx1, response, idx2, selection_options = self.getting_options_and_parameters()
        if self.response.done:
            return
        if type(idx2) is int:
            item = create_firebase_todo_calendar(task_id=selection_options[idx2])
        else:
            item = create_firebase_todo_calendar(title=idx2)
        response.insert(idx1, item)
        DiscordWrapper.fire_b.set_property('today-task', self.author.id, response)
        await self.list_action()

    async def set_action(self):
        idx1, response, idx2, selection_options = self.getting_options_and_parameters()
        if self.response.done:
            return
        deleted_item: Dict = response[idx1]
        if deleted_item['cal_id'] is not None:
            self.gcal.delete_calendar(response[idx1])
        if type(idx2) is int:
            response[idx1] = create_firebase_todo_calendar(task_id=selection_options[idx2])
        else:
            response[idx1] = create_firebase_todo_calendar(title=idx2)
        DiscordWrapper.fire_b.set_property('today-task', self.author.id, response)
        await self.list_action()

    async def swap_action(self):
        idx1, idx2 = self.get_two_arguments()
        if not self.response.done:
            response = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
            swap_items(response, idx1, idx2, lambda: self.response.set_error_response(0))
            if not self.response.done:
                DiscordWrapper.fire_b.set_property('today-task', self.author.id, response)
            await self.list_action()

    def adjust_calendar(self, user_tasks, end_time):
        self.gcal.add_tasks_to_calendar(user_tasks, end_time, self.todo)
        DiscordWrapper.fire_b.set_discord_config({'end-time': {str(self.author.id): end_time.timestamp()}})
        DiscordWrapper.fire_b.set_property('today-task', self.author.id, user_tasks)
        self.response.set_state(True, True)

    async def build_action(self):
        state, hour, minute = self.parse_time_arguments()
        if state is not None:
            self.response.set_error_response(state, True)
            return

        user_tasks: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        end_time = get_datetime_from_hour_minute(hour, minute, self.gcal.timezone)
        self.adjust_calendar(user_tasks, end_time)

    async def remove_action(self):
        response: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        remove_items = [parse_int(i)
                        for i in self.args[1:] if parse_int(i) is not None]
        remove_items.sort(reverse=True)
        for i in remove_items:
            if i < len(response):
                self.gcal.delete_calendar(response[i])
                del response[i]
            else:
                self.response.set_error_response(0, False)
        DiscordWrapper.fire_b.set_property('today-task', self.author.id, response)
        await self.list_action()

    async def list_action(self, user_tasks=None):
        if user_tasks is None:
            user_tasks: List = DiscordWrapper.fire_b.get_property('today-task', self.author.id, [])
        self.set_raw_simple_tasks(user_tasks)
        response = create_message_todoist_and_title(self.raw_tasks, self.todo)
        self.response.add_response(response, done=True)

    def create_sch_action(self):
        return iterate_commands(self.args[0], [
            ('add', self.add_action), ('set', self.set_action),
            ('swap', self.swap_action), ('build', self.build_action),
            ('list', self.list_action), ('remove', self.remove_action),
            ('insert', self.insert_action)
        ], starts_with=False)

    async def sch_run(self):
        if len(self.args) > 0:
            method = self.create_sch_action()
            if method is not None:
                await method()
        else:
            self.response.set_error_response(0)

    async def run(self):
        if not self.response.done:
            if not self.gcal.is_logged_in():
                self.response.set_error_response(UserError.AUTHORIZATION_ERROR, True)
                return
            await self.sch_run()
