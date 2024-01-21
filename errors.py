class BotExceptions(Exception):
    pass


class DateInputError(BotExceptions):
    def __init__(self):
        super().__init__('Неправильный формат дат. Используйте дд.мм.гггг')
