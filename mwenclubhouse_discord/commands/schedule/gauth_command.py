from google.oauth2.credentials import Credentials

from mwenclubhouse_discord.commands.command import UserCommand
from mwenclubhouse_discord.common import UserResponse, create_simple_message
from mwenclubhouse_discord.features.calendar import MWCalendar
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class GAuthCommand(UserCommand):

    def __init__(self, message, response: UserResponse):
        super().__init__(message, response)
        self.arg: str = self.content[7:]
        self.gcal: MWCalendar = MWCalendar(self.author.id)

    def create_pickle(self):
        cred: Credentials | None = self.gcal.get_credentials()
        if cred and cred.valid:
            self.response.set_error_response(0, True)
            return
        is_created = self.gcal.set_credentials(self.arg)
        if is_created:
            response = create_simple_message("Authenticating User", "Successfully Logged into Google Account")
            self.response.add_response(response, True)
        else:
            self.response.set_error_response(0, True)

    def get_authorization(self):
        url = DiscordWrapper.gCal.get_flow().authorization_url()
        if url is not None and len(url) > 0:
            response = create_simple_message("Need Google Credentials", f'[Click Here]({url[0]})')
            self.response.add_response(response, True)
        else:
            self.response.set_error_response(0, True)

    def get_pickle_state(self):
        cred = self.gcal.get_credentials()
        response = create_simple_message("Not Logged In", "type $gauth auth to login")
        if cred:
            response = create_simple_message("Logged In", "You Are Logged In")
        self.response.add_response(response, True)

    async def run(self):
        if self.arg.startswith('state'):
            self.get_pickle_state()
        elif self.arg.startswith('auth'):
            self.get_authorization()
        else:
            self.create_pickle()
