class BotExceptions(Exception):
    pass


class DataBaseError(BotExceptions):
    def __init__(self):
        super().__init__()


class DateInputError(BotExceptions):
    def __init__(self):
        super().__init__('Неправильный формат дат. Используйте дд.мм.гггг')



