import telebot
from telebot import types # для указание типов
from typing import Dict
from db_functions import *
from users_states import UserCache
from keyboard_markups import my_markups
from db_config_reader import read_config
from datetime import datetime

API_TOKEN = read_config(filename='config.ini', section='api')['key']
name_tg = '@hist_museum_bot'
bot = telebot.TeleBot(API_TOKEN)
session, _ = database_init()
admins_dict = get_admins_ids_names_dict(session)
users_cache_dict: Dict[int, UserCache] = {}


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
            callback_button = types.InlineKeyboardButton(text=excursion.title, callback_data=f'excursion_admin.{excursion.id}')
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
            callback_button = types.InlineKeyboardButton(text=text, callback_data=f'window_admin.{window.id}')
            keyboard.add(callback_button)
        bot.send_message(message.chat.id, "На данный момент указано следующее расписание: 👇",
                         reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.callback_query_handler(func=lambda call: 'admin' not in call.data)
def user_choosing_excursion_window(call):
    if call.data == 'excursion_info':
        excursion_ids_and_names = sorted(list(get_current_excursions_ids_and_names(session)), key=lambda x: x[1])
        keyboard = types.InlineKeyboardMarkup()
        for i, id_and_name in enumerate(excursion_ids_and_names):
            callback_button = types.InlineKeyboardButton(text=id_and_name[1],
                                                         callback_data=f'excursion_choice.{id_and_name[0]}')
            keyboard.add(callback_button)
        bot.edit_message_text("На данный момент можно записаться на следующие экскурсии: 👇",
                              call.message.chat.id, call.message.id, reply_markup=keyboard)
    # по нажатию на конкретную экскурсию вываливаем актуальные даты
    elif call.data.startswith('excursion_choice'):
        excursion_id = int(call.data.split('.')[1])
        excursion_info = get_excursion_info_by_id(session, excursion_id) # title, description, duration
        windows_ids_and_dates = [(x[0], x[1].strftime("%d.%m.%Y")) for x in
                                 sorted(get_windows_ids_and_dates_by_excursion_id(session, excursion_id),
                                        key=lambda x: x[1])]
        keyboard = types.InlineKeyboardMarkup()
        for i, window_id_and_date in enumerate(windows_ids_and_dates):
            callback_button = types.InlineKeyboardButton(text=window_id_and_date[1],
                                                         callback_data=f'date_choice.{window_id_and_date[0]}')
            keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='Вернуться к выбору экскурсии',
                                                     callback_data='excursion_info')
        keyboard.add(callback_button)
        text = ''
        text += excursion_info[0] + '\n'
        text += excursion_info[1] + '\n'
        text += 'Длительность: ' + excursion_info[2] + 'мин.\n'
        text += "На данный момент можно записаться на следующие даты: 👇"
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)

    # по нажатию на конкретную дату продолжаем ветку через register_next_step_handler, уточняем детали
    elif call.data.startswith('date_choice'):
        users_cache_dict[call.message.chat.id] = UserCache(datetime.now())
        users_cache_dict[call.message.chat.id].window_id = int(call.data.split('.')[1])
        text = 'Как вас записать? (укажите имя)'
        bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(call.message, how_many)



@bot.message_handler(content_types=['text'])
def how_many(message):
    users_cache_dict[message.chat.id].contact_name = message.text
    users_cache_dict[message.chat.id].contact_link = message.from_user.username
    text = "Сколько вас?"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, confirm)


@bot.message_handler(content_types=['text'])
def confirm(message):
    info = [users_cache_dict[message.chat.id].window_id, users_cache_dict[message.chat.id].contact_link,
            users_cache_dict[message.chat.id].contact_name, message.text]
    # ожидаемые аргументы: сессия и [window_id, contact_link, contact_name, umber]
    # при успехе возвращаем объект окна расписания
    result = add_visit_into_window(session, info)
    if result:
        text = (f'🎉Поздравляю! Вы, {result.contact_name}, успешно записаны '
                f'на {result.date_time.strftime("%d.%m.%Y")} на экскурсию!.\n'
                f'Моя команда свяжется с вами в ближайшее время')
    else:
        text = '❌Возникла ошибка! Попробуйте заново или обратитесь к администратору '
    bot.send_message(message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: 'admin' in call.data)
def admin_functions(call):
    if 'excursion_admin' in call.data:
        this_exscursion = get_all_excursion_info_by_id(session, int(call.data.split('.')[1]))
        text = f'Экскурсия'
        text += 'Описание'
        text += 'Длительность'
        text += 'Окна'
        text += 'Заявки'
        excursion_id = call.data.split('.')[1]
        keyboard = types.InlineKeyboardMarkup()
        edit_excursion_btn = types.InlineKeyboardButton(text='Редактировать описание',
                                                        callback_data=f'edit_excursion.{excursion_id}')
        add_window_btn = types.InlineKeyboardButton(text='Добавить окно',
                                                    callback_data=f'add_window.{excursion_id}')
        del_window_btn = types.InlineKeyboardButton(text='Удалить окно',
                                                    callback_data=f'del_window.{excursion_id}')
        back_btn = types.InlineKeyboardButton(text='К списку экскурсий', callback_data=f'back')
        keyboard.add(edit_excursion_btn, add_window_btn, del_window_btn, back_btn)
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)
    elif 'window_admin' in call.data:
        text = f'Экскурсия'
        text += 'Описание'
        text += 'Длительность'
        if 'кто-то уже записался':
            text += 'Дата'
            text += 'Ссылка'
            text += 'Как зовут сколько их'
            back_btn = types.InlineKeyboardButton(text='К списку экскурсий', callback_data=f'back')
        else:
            window_id = call.data.split('.')[1]
            edit_window_btn = types.InlineKeyboardButton(text='Редактировать описание',
                                                            callback_data=f'edit_excursion.{excursion_id}')
            del_window_btn = types.InlineKeyboardButton(text='Удалить окно',
                                                        callback_data=f'del_window.{excursion_id}')


bot.infinity_polling()