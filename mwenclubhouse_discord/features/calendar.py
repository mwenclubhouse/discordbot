from datetime import datetime, timezone, timedelta

from googleapiclient.errors import HttpError

from mwenclubhouse_discord.features.todoist import MWTodoist, get_task_url
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle


def create_firebase_todo_calendar(task_id=None, calendar_id=None, title=None):
    return {'task_id': task_id, 'cal_id': calendar_id, 'title': title}


def create_event(name, description, start_time, end_time, time_zone):
    return {
        'start': {
            'dateTime': get_iso_from_datetime(start_time),
            'timeZone': time_zone
        },
        'end': {
            'dateTime': get_iso_from_datetime(end_time),
            'timeZone': time_zone
        },
        'summary': name,
        'description': description
    }


def create_cal_event_from_todoist(i, todo: MWTodoist, start, end, user_timezone):
    if i['task_id']:
        task = todo.get_item(i['task_id'])
        project = todo.get_project(task['project_id'])
        return create_event(project['project']['name'],
                            f"<a href='{get_task_url(i['task_id'])}'>"
                            f"{task['content']}"
                            f"</a>",
                            start, end, user_timezone)
    else:
        return create_event(i['title'], "", start, end, user_timezone)


def edit_event(i, service, details):
    if i['cal_id'] is not None:
        service.events().update(
            calendarId="primary",
            eventId=i['cal_id'],
            body=details
        ).execute()
        return
    i['cal_id'] = service.events().insert(
        calendarId="primary",
        body=details,
        sendNotifications=True,
    ).execute()['id']


def update_calendar(author_id):
    pass


class MWCalendar:

    def __init__(self, author_id):
        self.author_id = author_id
        self.cred = self.get_credentials()
        self.service = self.get_service()

    def is_logged_in(self):
        return self.cred is not None and self.service is not None

    def get_credentials(self):
        location = f'discord/{self.author_id}/token.pickle'
        raw_data = DiscordWrapper.fire_b.get_file(location)
        if raw_data:
            response = pickle.loads(raw_data)
            if response and response.expired:
                if response.refresh_token:
                    response.refresh(Request())
                else:
                    response = None
            return response
        return None

    def get_service(self):
        if self.cred:
            return build('calendar', 'v3', credentials=self.cred)
        return None

    def set_credentials(self, code: str) -> bool:
        flow = DiscordWrapper.gCal.get_flow()
        try:
            flow.fetch_token(code=code)
            self.cred = flow.credentials
            response = pickle.dumps(self.cred)
            location = f'discord/{self.author_id}/token.pickle'
            DiscordWrapper.fire_b.upload_file(location, response)
            return True
        except:
            return False

    @property
    def timezone(self):
        if self.service:
            response = self.service.settings().get(setting="timezone").execute()
            if response:
                return response['value']
        return None

    def get_events(self, end):
        now = datetime.utcnow().isoformat() + 'Z'
        if end is None:
            end = datetime.utcnow() + timedelta(hours=24)
        if self.service:
            events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                                       timeMax=get_iso_from_datetime(end),
                                                       singleEvents=True,
                                                       orderBy='startTime').execute()
            return events_result.get('items', [])
        return []

    def delete_calendar(self, item):
        try:
            if item['cal_id'] is not None:
                self.service.events().delete(calendarId='primary', eventId=item['cal_id']).execute()
                item['cal_id'] = None
        except HttpError:
            return

    def complete_calendar(self, item):
        if self.service:
            details = self.service.events().get(calendarId='primary', eventId=item['cal_id']).execute()
            user_timezone = self.timezone
            if user_timezone is None or details is None:
                return
            now_time = datetime.utcnow().isoformat() + 'Z'
            details['end'] = {'dateTime': now_time, 'timeZone': user_timezone}
            self.service.events().update(calendarId='primary', eventId=item['cal_id'],
                                         body=details).execute()

    def clean_calendar(self, items):
        i, last_item = 0, None
        while i < len(items):
            if last_item is not None and last_item['task_id'] and last_item['task_id'] == items[i]['task_id']:
                self.delete_calendar(items[i])
                del items[i]
            else:
                last_item = items[i]
                i += 1

    def add_tasks_to_calendar(self, items, end, todo: MWTodoist, set_start_time_now=True):
        if self.service:
            self.clean_calendar(items)
            events = MyEventQueue(items, self.get_events(end), end, set_start_time_now)
            user_timezone = self.timezone
            for task, start_time, end_time in events:
                details = create_cal_event_from_todoist(task, todo, start_time, end_time, user_timezone)
                edit_event(task, self.service, details)
            return events.end_time
        return None


def parse_google_cal_event_time(event, key):
    return datetime.strptime(event[key]['dateTime'], "%Y-%m-%dT%H:%M:%S%z")


def get_event_duration(event, min_start=None):
    start = parse_google_cal_event_time(event, 'start')
    if min_start is not None:
        start = start if start.timestamp() > min_start.timestamp() else min_start
    end = parse_google_cal_event_time(event, 'end')
    return end.timestamp() - start.timestamp()


def time_in_event(event, t):
    start = parse_google_cal_event_time(event, 'start')
    end = parse_google_cal_event_time(event, 'end')
    return start.timestamp() <= t.timestamp() <= end.timestamp()


def event_overlap(e1, e2):
    start = parse_google_cal_event_time(e1, 'start')
    end = parse_google_cal_event_time(e1, 'end')
    return time_in_event(e2, start) or time_in_event(e2, end)


def get_iso_from_datetime(datetime_item):
    return datetime_item.astimezone(timezone.utc).isoformat().replace("+00:00", 'Z')


class MyEventQueue:

    def __init__(self, tasks, events, end_time, set_start_time_now=True):
        self.tasks = tasks
        self.events = events

        self.calendar_set = self.get_calendar_set()
        self.start_time = self.get_start_time(set_start_time_now)
        self.end_time = self.get_end_time(end_time)
        self.tasks_duration = self.create_duration_stack()

        self.iterated_items = []

    def get_calendar_set(self):
        calendar_id = set()
        for i in self.tasks:
            calendar_id.add(i['cal_id'])
        return calendar_id

    def get_start_time(self, set_start_time_now):
        if set_start_time_now:
            return datetime.now()
        min_value = datetime.now()
        for item in self.events:
            if item['id'] in self.calendar_set:
                start = parse_google_cal_event_time(item, 'start')
                if min_value.timestamp() > start.timestamp():
                    min_value = start
        return min_value

    def get_end_time(self, end_time):
        self.end_time = datetime.now() if end_time is None else end_time
        space_allocated = self.get_available_time(min_val=None)
        if space_allocated <= 0:
            seconds = 60 * 60 * len(self.tasks) - space_allocated
            end_time += timedelta(seconds=seconds)
        return end_time

    def get_available_time(self, min_val=None):
        calendar_set = self.calendar_set
        time_available = self.end_time.timestamp() - self.start_time.timestamp()
        for i in self.events:
            if i['id'] not in calendar_set:
                time_available -= get_event_duration(i, min_start=self.start_time)
        if min_val is not None:
            time_available = time_available if time_available > min_val else min_val
        return time_available

    def create_duration_stack(self):
        if len(self.tasks) == 0:
            return []
        duration = self.get_available_time(min_val=0) / len(self.tasks)
        return [duration for _ in self.tasks]

    def parse_next_calendar_event(self, calendar_set):
        for i, item in enumerate(self.events):
            if item['id'] not in calendar_set:
                self.events = self.events[i + 1:]
                return item
        return None

    def insert_task_to_front(self, t, d):
        item = create_firebase_todo_calendar(task_id=t['task_id'])
        self.tasks.insert(0, item)
        self.tasks_duration.insert(0, d)
        return self.tasks[0], self.tasks_duration[0]

    def decrement_time(self, start_time, calendar_set):
        t, d = self.tasks[0], self.tasks_duration[0]

        next_event = self.parse_next_calendar_event(calendar_set)
        next_start = None

        # Check Event Start
        while next_event and time_in_event(next_event, start_time):
            start_time = parse_google_cal_event_time(next_event, 'end')
            next_event = self.parse_next_calendar_event(calendar_set)

        # Check Event End
        if next_event and time_in_event(next_event, start_time + timedelta(seconds=d)):
            d = parse_google_cal_event_time(next_event, 'start').timestamp() - start_time.timestamp()
            self.tasks_duration[0] -= d
            next_start = parse_google_cal_event_time(next_event, 'end')
            t, d = self.insert_task_to_front(t, d)

        # Decrement -> Move to Next Task
        self.tasks = self.tasks[1:]
        self.tasks_duration = self.tasks_duration[1:]

        end_time = start_time + timedelta(seconds=d)
        next_start = end_time if next_start is None else next_start
        return start_time, end_time, t, next_start

    def __iter__(self):
        start_time = self.start_time
        calendar_set = self.calendar_set
        while len(self.tasks) > 0:
            start_time, end_time, t, next_start = self.decrement_time(start_time, calendar_set)
            yield t, start_time, end_time
            start_time = next_start
