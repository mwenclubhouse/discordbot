import todoist
import os
from datetime import datetime, timedelta
import pytz

from todoist.models import Item

week_day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def get_date(item, timezone=None):
    if item['due'] is None:
        return None
    d = datetime.strptime(item['due']['date'], '%Y-%m-%d')
    if timezone is not None:
        tz = pytz.timezone(timezone)
        d = tz.localize(d)
    return d


def get_weekday_index(index):
    return (index + 1) % 7


def get_parsed_date(task, parentheses=False, timezone=None):
    item_time = get_date(task, timezone=timezone)
    now_time = datetime.now() if timezone is None else datetime.now(tz=pytz.timezone(timezone))
    if item_time is None:
        return ''
    num_days = int((item_time - now_time) / timedelta(days=1))
    response = ''
    if num_days < 0:
        response = f'{-num_days} day{"s" if -num_days > 1 else ""} ago'
    elif num_days == 0:
        response = f'Today'
    elif num_days == 1:
        response = f'Tomorrow'
    else:
        if get_weekday_index(now_time.weekday()) >= get_weekday_index(item_time.weekday()):
            response += 'Next '
        index = get_weekday_index(item_time.weekday())
        response += week_day_names[index]
    return f'({response})' if parentheses and response != '' else response


def get_task_url(task_id):
    return f'https://todoist.com/showTask?id={task_id}'


class MWTodoist:

    def __init__(self):
        api_value = os.getenv('TODOIST_API')
        self.api = None if api_value is None else todoist.TodoistAPI(api_value)
        self.sync_api()

    def sync_api(self):
        try:
            if self.api is not None:
                self.api.sync()
        except AttributeError:
            pass

    def commit_api(self):
        try:
            if self.api is not None:
                self.api.commit()
        except AttributeError:
            pass

    def is_section_in_progress(self, section_id):
        try:
            if section_id is None:
                return True
            section = None if self.api is None else self.api.sections.get_by_id(section_id)
            return section is None or section['name'] not in ['Finished']
        except AttributeError:
            return False

    def get_parent_task(self, item_id, item=None):
        try:
            item = self.get_item(item_id) if item is None else item
            if 'parent_id' in item and item['parent_id'] is not None:
                return self.get_parent_task(item['parent_id'])
            return item
        except AttributeError:
            return None

    def move_task_to_section(self, name, task: Item):
        try:
            destination = self.get_section_by_name(name, task['project_id'])
            if destination is not None:
                task.update(content='Another One bang')
                self.api.items.move(task['id'], section_id=destination['id'])
        except AttributeError:
            pass

    def get_section_by_name(self, name, project_id):
        try:
            for i in self.api.sections.all():
                if i['project_id'] == project_id and i['name'] == name:
                    return i
            return None
        except AttributeError:
            return None

    def get_upcoming_tasks(self):
        def filter_tasks(item):
            item_time = get_date(item)
            within_range = item_time is not None and item_time <= datetime.now() + timedelta(days=7)
            return within_range and item['date_completed'] is None

        def sort_task(item):
            key_value = get_date(item, timezone=self.get_timezone())
            return key_value if key_value is not None else datetime.now()

        try:
            query_tasks = [] if self.api is None else self.api.items.all(filt=filter_tasks)
            response = [i for i in query_tasks if self.is_section_in_progress(i['section_id'])]
            return sorted(response, key=sort_task)
        except AttributeError:
            return []

    def get_project(self, project_id):
        try:
            project = None if self.api is None else self.api.projects.get(project_id)
            return {} if project is None else project
        except AttributeError:
            return {}

    def get_section(self, section_id):
        try:
            section = self.api.sections.get(section_id)
            return {} if section is None else section
        except AttributeError:
            return {}

    def get_item(self, item_id):
        try:
            item = self.api.items.get(item_id)
            return {} if item is None else item['item']
        except AttributeError:
            return {}

    def iterate_tasks(self, items):
        for i in items:
            try:
                parent_tasks = self.get_parent_task(None, i)
                yield parent_tasks
            except AttributeError:
                pass

    def iterate_parent_project_and_tasks(self, tasks):
        for i in tasks:
            try:
                project = self.get_project(i['project_id'])
                due_date = get_parsed_date(i)
                url = get_task_url(i)
                yield i, project, '' if due_date is None else f'({due_date})', url
            except AttributeError:
                pass

    def convert_list_id_to_items(self, list_ids):
        for i in list_ids:
            try:
                item = self.api.items.get(i)
                yield item
            except AttributeError:
                pass

    def get_timezone(self):
        try:
            return self.api['user']['tz_info']['timezone']
        except AttributeError:
            return None
