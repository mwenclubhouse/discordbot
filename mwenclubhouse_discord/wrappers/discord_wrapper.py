from .calendar_wrapper import CalendarWrapper
from .firebase_wrapper import FirebaseWrapper


class DiscordWrapper:
    client = None
    fire_b: FirebaseWrapper = None
    gCal: CalendarWrapper = None
