from mwenclubhouse_discord.commands.command import UserCommand
from mwenclubhouse_discord.common import create_simple_message
from mwenclubhouse_discord.common.error import UserError


class UserCommandLeave(UserCommand):

    def __init__(self, author, content, response):
        super().__init__(author, content, response)
        self.arguments = content[7:]

    def leave_single_channel(self):
        self.parse_input_set_head('ls', idx_none=UserError.UE_IVD_NUM, category_none=UserError.CE_TYPE_LS_CC)
        if not self.response.done and self.head is None:
            self.response.set_error_response(UserError.CE_NF)

        if not self.response.done:
            response = create_simple_message('Success!', f'leaving {self.head}', self.response.response_tail)
            self.response.add_permissions(self.author, self.head, False)
            self.response.set_success_response(response)

        if not self.response.done:
            self.response.set_error_response(UserError.CE_NF)

    async def run(self):
        args = self.arguments.split()
        if len(args) == 0:
            self.idx = ''
            self.leave_single_channel()
        else:
            for i in self.arguments.split():
                self.idx = i
                self.leave_single_channel()
                self.response.done = False
        self.response.done = True
