import todoist
import os
from datetime import datetime, timedelta

from todoist.models import Item

week_day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


def get_date(item):
    if item['due'] is None:
        return None
    return datetime.strptime(item['due']['date'], '%Y-%m-%d')


def get_parsed_date(task, parentheses=False):
    item_time = get_date(task)
    if item_time is None:
        return ''
    num_days = int((item_time - datetime.now()) / timedelta(days=1))
    response = ''
    if num_days < 0:
        response = f'{-num_days} day{"s" if -num_days > 1 else ""} ago'
    elif num_days == 0:
        response = f'Today'
    elif num_days == 1:
        response = f'Tomorrow'
    else:
        if datetime.now().weekday() >= item_time.weekday():
            response += 'Next '
        response += week_day_names[item_time.weekday()]
    return f'({response})' if parentheses and response != '' else response


def get_task_url(task_id):
    return f'https://todoist.com/showTask?id={task_id}'


class MWTodoist:

    def __init__(self):
        api_value = os.getenv('TODOIST_API')
        self.api = None if api_value is None else todoist.TodoistAPI(api_value)
        self.sync_api()

    def sync_api(self):
        if self.api is not None:
            self.api.sync()

    def commit_api(self):
        if self.api is not None:
            self.api.commit()

    def is_section_in_progress(self, section_id):
        if section_id is None:
            return True
        section = None if self.api is None else self.api.sections.get_by_id(section_id)
        return section is None or section['name'] not in ['Finished']

    def get_parent_task(self, item_id, item=None):
        item = self.get_item(item_id) if item is None else item
        if 'parent_id' in item and item['parent_id'] is not None:
            return self.get_parent_task(item['parent_id'])
        return item

    def move_task_to_section(self, name, task: Item):
        destination = self.get_section_by_name(name, task['project_id'])
        if destination is not None:
            task.update(content='Another One bang')
            self.api.items.move(task['id'], section_id=destination['id'])

    def get_section_by_name(self, name, project_id):
        for i in self.api.sections.all():
            if i['project_id'] == project_id and i['name'] == name:
                return i
        return None

    def get_upcoming_tasks(self):
        def filter_tasks(item):
            item_time = get_date(item)
            return False if item_time is None else (datetime.now() + timedelta(days=7)) >= item_time

        def sort_task(item):
            return get_date(item)

        query_tasks = [] if self.api is None else self.api.items.all(filt=filter_tasks)
        response = [i for i in query_tasks if self.is_section_in_progress(i['section_id'])]
        return sorted(response, key=sort_task)

    def get_project(self, project_id):
        project = None if self.api is None else self.api.projects.get(project_id)
        return {} if project is None else project

    def get_section(self, section_id):
        section = self.api.sections.get(section_id)
        return {} if section is None else section

    def get_item(self, item_id):
        item = self.api.items.get(item_id)
        return {} if item is None else item['item']

    def iterate_tasks(self, items):
        for i in items:
            parent_tasks = self.get_parent_task(None, i)
            yield parent_tasks

    def iterate_parent_project_and_tasks(self, tasks):
        for i in tasks:
            project = self.get_project(i['project_id'])
            due_date = get_parsed_date(i)
            url = get_task_url(i)
            yield i, project, '' if due_date is None else f'({due_date})', url

    def convert_list_id_to_items(self, list_ids):
        for i in list_ids:
            item = self.api.items.get(i)
            yield item
