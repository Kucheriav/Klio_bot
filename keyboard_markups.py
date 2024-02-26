from telebot import types # для указание типов


class MyMarkupsFabric:
    about_museum_btn = types.KeyboardButton("🏛️О музее")
    about_bot_btn = types.KeyboardButton("🤖О боте")
    about_team_btn = types.KeyboardButton("🔥Наш актив")
    about_excursions_btn = types.KeyboardButton('❗Узнать про экскурсии и записаться')
    edit_excursion_btn = types.KeyboardButton("ℹ️Виды экскурсий")
    edit_timetable_btn = types.KeyboardButton("📝Расписание")

    def get_user_menu(self):
        user_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        user_markup.add(self.about_museum_btn, self.about_bot_btn, self.about_team_btn, self.about_excursions_btn)
        return user_markup

    def get_admin_menu(self):
        admin_markup = self.get_user_menu()
        admin_markup.add(self.edit_excursion_btn)
        admin_markup.add(self.edit_timetable_btn)
        return admin_markup

    def get_buttons_text(self):
        res = []
        for attr in dir(MyMarkupsFabric):
            if '_btn' in attr:
                res.append(getattr(MyMarkupsFabric, attr).text)
        return res


my_markups = MyMarkupsFabric()
