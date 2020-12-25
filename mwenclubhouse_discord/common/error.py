all_error_types = [
    {
        'title': 'Parsing Error',
        'msg': "Please type a number representing a Category Channel you want to enter",
    },
    {
        'title': 'User Error',
        'msg': "Please type `ls` to list possible Categories",
    },
    {
        'title': "Computer Error",
        'msg': "Please type `ls` again."
    },
    {
        'title': 'User Error',
        'msg': 'You cannot `cd` inside a non Category Channel'
    },
    {
        'title': 'User Error',
        'msg': 'Invalid Channel ID. Please Input a Number'
    },
    {
        'title': 'Computer Error',
        'msg': 'Type `ls` to list channels inside category channel.'
    },
    {
        'title': 'Computer Error',
        'msg': 'Channel is Not Found'
    }
]


class UserError:
    PS_ENTER_NUM = 0
    UE_ENTER_LS = 1
    CE_TYPE_LS_A = 2
    UE_CD = 3
    UE_IVD_NUM = 4
    CE_TYPE_LS_CC = 5
    CE_NF = 6


