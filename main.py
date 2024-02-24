import telebot
from telebot import types # для указание типов
from db_functions import *
from users_states import User
from keyboard_markups import my_markups
from db_config_reader import read_config


API_TOKEN = read_config(filename='config.ini', section='api')['key']
name_tg = '@hist_museum_bot'
bot = telebot.TeleBot(API_TOKEN)
session, _ = database_init()
admins_dict = get_admins_ids_names_dict(session)
users_states = dict()


@bot.message_handler(content_types=['text'])
def work(message):
    if message.text == '/start' and message.from_user.id in admins_dict:
        text = f'Привет, администратор {admins_dict[message.from_user.id]}! Клио приветствует тебя👋\nЧто-то нужно?'
        bot.send_photo(message.chat.id, open('menu.jpg', 'rb'), caption=text)
        bot.send_message(message.chat.id, 'Выберите одну из команд в меню: 👇', reply_markup=my_markups.get_admin_menu())

    elif message.text == '/start':
        text = 'Привет! 👋 Я - Клио! Я интерактивный помощник Исторического музея школы №13.'
        bot.send_photo(message.chat.id, open('menu.jpg', 'rb'), caption=text)
        bot.send_message(message.chat.id, 'Выберите одну из команд в меню: 👇', reply_markup=my_markups.get_user_menu())

    elif message.text == my_markups.about_museum_btn.text:
        text = ("Исторический музей школы №13 создан в 2021 году. Номер свидетельства …… "
                "Музей имеет официальный статус и зарегистрирован на портале Школьных музеев. "
                "Наш музей совсем молодой, поэтому оживление памяти в формате интерактивных опросов, "
                "креативных обзоров и  увлекательных экскурсий - это про нас!")
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_bot_btn.text:
        text = "Имя Клио я получил в честь музы истории в древнегреческой мифологии."
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_team_btn.text:
        text = ("Наш музейный актив - увлеченные, заинтересованные ребята! Знакомьтесь! Бекетова Влада, "
                "Иващенко Лиза, Мосина Вика, Кондрашов Паша, Бессуднов Артём, Коцебук Настя, Синица Лера, "
                "Арсений - экскурсоводы и активисты музея.")
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_excursions_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="📝Запись на экскурсию", callback_data='excursion_info')
        keyboard.add(callback_button)
        text = ("Записаться на экскурсию можно в кабинете 301 на третьем этаже или нажав на кнопку ниже. "
                "Мы всегда рады вас видеть и подберем удобное время!")
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

    elif message.text == my_markups.edit_excursion_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        excursions = get_all_excursions(session)
        for i, excursion in enumerate(excursions):
            callback_button = types.InlineKeyboardButton(text=excursion[0], callback_data=f'excursion_admin.{i}')
            keyboard.add(callback_button)
        bot.send_message(message.chat.id, "На данный момент указаны следующие экскурсии: 👇",
                         reply_markup=keyboard)

    elif message.text == my_markups.edit_timetable_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        windows = get_all_current_windows(session)
        for i, window in enumerate(windows):
            text = window.title + ' ' + window.date_time.strftime('%d.%m.%Y')
            if window.contact_link:
                text = '✅' + text
            else:
                text = '☑️' + text
            callback_button = types.InlineKeyboardButton(text=text, callback_data=f'timetable_admin.{i}')
            keyboard.add(callback_button)
        bot.send_message(message.chat.id, "На данный момент указано следующее расписание: 👇",
                         reply_markup=keyboard)

    else:
        print(message.text)
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.callback_query_handler(func=lambda call: True)
def user_choosing_excursion_window(call):
    if call.data == 'excursion_info':
        users_states[call.message.chat.id] = User()
        windows_names = sorted(list(get_current_windows_names(session)))
        users_states[call.message.chat.id].actual_excursions = windows_names[:]
        keyboard = types.InlineKeyboardMarkup()
        for i, name in enumerate(windows_names):
            callback_button = types.InlineKeyboardButton(text=name, callback_data=f'excursion_choice.{i}')
            keyboard.add(callback_button)
        bot.edit_message_text("На данный момент можно записаться на следующие экскурсии: 👇",
                              call.message.chat.id, call.message.id, reply_markup=keyboard)
    # по нажатию на конкретную экскурсию вываливаем актуальные даты
    elif call.data.startswith('excursion_choice'):
        excursion_choice = users_states[call.message.chat.id].actual_excursions[int(call.data.split('.')[1])]
        users_states[call.message.chat.id].excursion_choice = excursion_choice
        dates = sorted([x.strftime("%d.%m.%Y") for x in get_actual_dates_by_name(session, excursion_choice)])
        users_states[call.message.chat.id].actual_dates = dates[:]
        keyboard = types.InlineKeyboardMarkup()
        for i, date in enumerate(dates):
            callback_button = types.InlineKeyboardButton(text=date,
                                                         callback_data=f'date_choice.{i}')
            keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='Вернуться к выбору экскурсии',
                                                     callback_data='excursion_info')
        keyboard.add(callback_button)
        text = ''
        text += excursion_choice + '\n'
        text += get_description_by_title(session, excursion_choice)+ '\n'
        text += "На данный момент можно записаться на следующие даты: 👇"
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)

    # по нажатию на конкретную дату продолжаем ветку через register_next_step_handler, уточняем детали
    elif call.data.startswith('date_choice'):
        date_choice = users_states[call.message.chat.id].actual_dates[int(call.data.split('.')[1])]
        users_states[call.message.chat.id].date_choice = date_choice
        text = 'Как вас записать? (укажите имя)'
        bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(call.message, how_many)



@bot.message_handler(content_types=['text'])
def how_many(message):
    users_states[message.chat.id].contact_name = message.text
    users_states[message.chat.id].contact_link = message.from_user.username
    text = "сколько вас?"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, confirm)


@bot.message_handler(content_types=['text'])
def confirm(message):
    number = message.text
    window_id = window_id_by_title_and_date(session, users_states[message.chat.id].excursion_choice,
                                            users_states[message.chat.id].date_choice)
    # ожидаемые аргументы: сессия и [window_id, contact_link, contact_name,  number]
    result = add_visit_into_window(session, [window_id, users_states[message.chat.id].contact_link,
                                             users_states[message.chat.id].contact_name, number])
    if result == 'ok':
        text = (f'🎉Поздравляю! Вы, {users_states[message.chat.id].contact_name}, успешно записаны '
                f'на {users_states[message.chat.id].date_choice} '
                f'на экскурсию {users_states[message.chat.id].excursion_choice}.\n'
                f'Моя команда свяжется с вами в ближайшее время')
    else:
        text = '❌Возникла ошибка! Попробуйте заново или обратитесь к администратору '
    bot.send_message(message.chat.id, text=text)


bot.infinity_polling()