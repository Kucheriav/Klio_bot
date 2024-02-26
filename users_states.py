from enum import Enum

class UserState(Enum):
    MAIN_MENU = 1
    CHOOSING = 2
    RESULT = 3

class UserCache:
    def __init__(self, date):
        self.state = UserState.MAIN_MENU
        self.date = date
        self.contact_name = ''
        self.contact_link = ''
        self.date_choice = ''
        self.window_id = ''





