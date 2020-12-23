import os


def get_environment(name):
    value = os.getenv(name)
    return '' if value is None else value


ENVIRONMENT = {
    'general': get_environment('ANNOUNCEMENT_CHANNEL_ID')
}
