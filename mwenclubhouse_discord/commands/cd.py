from mwenclubhouse_discord.commands.ls import UserCommandLS
from mwenclubhouse_discord.common.utils import *
from mwenclubhouse_discord.common.error import UserError
from mwenclubhouse_discord.wrappers.discord_wrapper import DiscordWrapper


class UserCd(UserCommandLS):

    def __init__(self, author, content, response, idx=None):
        super().__init__(author, content, response)
        self.idx = self.content[4:] if idx is None else idx

    def handle_no_idx(self):
        back_to_root = self.idx in ['', '..']
        if back_to_root:
            DiscordWrapper.fire_b.clear_selected('ls', self.author.id)
            DiscordWrapper.fire_b.set_property('location', self.author.id, '')
        if self.idx == '.' or back_to_root:
            self.response.set_success_response(super().get_response())

    def handle_parse_input(self):
        super().parse_input('ls', UserError.PS_ENTER_NUM, UserError.UE_ENTER_LS)

    def handle_category(self):
        if self.head is None:
            self.response.set_error_response(UserError.CE_TYPE_LS_A)
        elif type(self.head) is not CategoryChannel:
            self.response.set_error_response(UserError.UE_CD)

    def handle_new_location(self):
        DiscordWrapper.fire_b.set_property('location', self.author.id, self.head.id)
        self.set_raw_simple_category(self.head.channels)
        # self.category = self.head.channels
        self.response.set_success_response(super().get_response())

    def run(self):
        if not self.response.done:
            steps = [self.handle_no_idx, self.handle_parse_input,
                     self.handle_category, self.handle_new_location]
            for i in steps:
                i()
                if self.response.done:
                    return
