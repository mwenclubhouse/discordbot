import os
from google_auth_oauthlib.flow import InstalledAppFlow

scopes = ['https://www.googleapis.com/auth/calendar']


class CalendarWrapper:

    def __init__(self):
        cred_location = os.getenv('CAL_APPLICATION_CREDENTIALS')
        self.cred_location = cred_location

    def get_flow(self):
        return InstalledAppFlow.from_client_secrets_file(
            self.cred_location,
            scopes,
            redirect_uri="https://api.matthewwen.com/oauth/google/code"
        )
