import telebot
from telebot import types
from telebot.types import Message, CallbackQuery
from typing import Dict
from time import sleep
from db_functions import *
from users_states import UserCache
from keyboard_markups import my_markups
from db_config_reader import read_config
from datetime import datetime
from log_writer import setup_logger


logger = setup_logger(__name__)
API_TOKEN = read_config(filename='config.ini', section='api')['key']
name_tg = '@hist_museum_bot'
bot = telebot.TeleBot(API_TOKEN)
admins_dict = get_admins()
events_listeners_chat_id_list = [admins_dict[x].tg_chat_id for x in admins_dict
                                 if admins_dict[x].is_tracking_events is True]
users_cache_dict: Dict[int, UserCache] = {}
menu_buttons_text = my_markups.get_buttons_text()


@bot.message_handler(content_types=['text'])
def work(message: Message):
    if message.text == '/start' and message.from_user.id in admins_dict:
        if not admins_dict[message.from_user.id].tg_chat_id or \
                admins_dict[message.from_user.id].tg_chat_id != message.chat.id:
            update_user_chat_id(message.from_user.id, message.chat.id)

        logger.debug(f'Admin {admins_dict[message.from_user.id].name} started a dialog')

        text = f'Привет, администратор {admins_dict[message.from_user.id].name}! Клио приветствует тебя👋\nЧто-то нужно?'
        bot.send_photo(message.chat.id, open('menu.jpg', 'rb'), caption=text)
        bot.send_message(message.chat.id, 'Выберите одну из команд в меню: 👇', reply_markup=my_markups.get_admin_menu())

    elif message.text == '/start':

        logger.debug(f'new user started a dialog')

        text = 'Привет! 👋 Я - Клио! Я интерактивный помощник Исторического музея школы №13.'
        bot.send_photo(message.chat.id, open('menu.jpg', 'rb'), caption=text)
        bot.send_message(message.chat.id, 'Выберите одну из команд в меню: 👇', reply_markup=my_markups.get_user_menu())

    elif message.text == my_markups.about_museum_btn.text:
        text = 'Исторический музей школы №13 создан в 2021 году. Свидетельство №20557. Музей имеет официальный ' \
               'статус, зарегистрирован на портале Школьных музеев и имеет статус Школьного Музея Победы.\nТакже мы ' \
               'являемся победителями Всероссийского конкурса школьных музеев "Школьный музей - взгляд в будущее".\n' \
               'Наш музей совсем молодой, поэтому оживление памяти в формате интерактивных опросов, креативных ' \
               'обзоров и увлекательных экскурсий - это про нас!'
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_bot_btn.text:
        text = "Имя Клио я получил в честь музы истории в древнегреческой мифологии."
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_team_btn.text:
        text = ("Наш музейный актив - увлеченные, заинтересованные ребята! Знакомьтесь! Бекетова Влада, "
                "Иващенко Лиза, Мосина Вика, Кондрашов Паша, Бессуднов Артём, Коцебук Настя, Синица Лера, "
                "Арсений Юдин - экскурсоводы и активисты музея.")
        bot.send_message(message.chat.id, text)

    elif message.text == my_markups.about_excursions_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="📝Запись на экскурсию", callback_data='user_excursion_info')
        keyboard.add(callback_button)
        text = ("Записаться на экскурсию можно в кабинете 301 на третьем этаже или нажав на кнопку ниже. "
                "Мы всегда рады вас видеть!")
        bot.send_message(message.chat.id, text=text, reply_markup=keyboard)

    elif message.text == my_markups.edit_excursion_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        excursions = get_all_excursions()
        for i, excursion in enumerate(excursions):
            callback_button = types.InlineKeyboardButton(text=excursion.title,
                                                         callback_data=f'excursion_admin.{excursion.id}')
            keyboard.add(callback_button)
        callback_button = types.InlineKeyboardButton(text='Добавить новый вид экскурсии',
                                                     callback_data=f'excursion_admin.add')
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, "На данный момент указаны следующие экскурсии: 👇",
                         reply_markup=keyboard)

    # elif message.text == my_markups.edit_timetable_btn.text:
    #     keyboard = types.InlineKeyboardMarkup()
    #     windows = sorted(get_all_current_windows(), key=lambda window: window.date_time)
    #     for i, window in enumerate(windows):
    #         if len(window.title) > 35:
    #             text = window.title[:35] + '... ' + window.date_time.strftime('%d.%m.%Y %H:%M')
    #         else:
    #             text = window.title + ' ' + window.date_time.strftime('%d.%m.%Y %H:%M')
    #         if window.contact_link:
    #             text = '✅' + text
    #         else:
    #             text = '☑️' + text
    #         callback_button = types.InlineKeyboardButton(text=text, callback_data=f'window_admin.{window.id}')
    #         keyboard.add(callback_button)
    #     bot.send_message(message.chat.id, "На данный момент указано следующее расписание: 👇",
    #                      reply_markup=keyboard)

    elif message.text == my_markups.events_managment_btn.text:
        keyboard = types.InlineKeyboardMarkup()
        if message.chat.id in events_listeners_chat_id_list:
            text = 'Сейчас вам приходят уведомления при записи на экскурсию. ' \
                   'Нажмите кнопку, чтобы отписаться от обновлений'
            unsign_button = types.InlineKeyboardButton(text='Отписаться', callback_data=f'events.no')
            keyboard.add(unsign_button)
        else:
            text = 'Сейчас вам не приходят уведомления при записи на экскурсию. ' \
                   'Нажмите кнопку, чтобы подписаться на обновления'
            sign_button = types.InlineKeyboardButton(text='Подписаться', callback_data=f'events.yes')
            keyboard.add(sign_button)
        bot.send_message(message.chat.id, text, reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.callback_query_handler(func=lambda call: 'user' in call.data)
def user_choosing_excursion_window(call: CallbackQuery):
    if call.data == 'user_excursion_info':
        logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to read about all excursions')
        excursion_ids_and_names = sorted(list(get_current_excursions_ids_and_names()), key=lambda x: x[1])
        keyboard = types.InlineKeyboardMarkup()
        for i, id_and_name in enumerate(excursion_ids_and_names):
            callback_button = types.InlineKeyboardButton(text=id_and_name[1],
                                                         callback_data=f'user_excursion_choice.{id_and_name[0]}')
            keyboard.add(callback_button)
        bot.edit_message_text("На данный момент можно записаться на следующие экскурсии: 👇",
                              call.message.chat.id, call.message.id, reply_markup=keyboard)
    # по нажатию на конкретную экскурсию вываливаем актуальные даты
    elif call.data.startswith('user_excursion_choice'):

        excursion_id = int(call.data.split('.')[1])
        excursion_info = get_excursion_info_by_id(excursion_id)  # title, description, duration

        logger.debug(f'{call.from_user.username} from {call.message.chat.id} chose {excursion_info[0]}')

        # windows_ids_and_dates = [(x[0], x[1].strftime("%d.%m.%Y %H:%M")) for x in
        #                          sorted(get_windows_ids_and_dates_by_excursion_id(excursion_id),
        #                                 key=lambda x: x[1])]
        keyboard = types.InlineKeyboardMarkup()
        # for i, window_id_and_date in enumerate(windows_ids_and_dates):
        #     callback_button = types.InlineKeyboardButton(text=window_id_and_date[1],
        #                                                  callback_data=f'user_date_choice.{window_id_and_date[0]}')
        #     keyboard.add(callback_button)

        callback_button_yes = types.InlineKeyboardButton(text='Интересно, записывайте',
                                                          callback_data='user_date_choice')
        callback_button_back = types.InlineKeyboardButton(text='Вернуться к выбору экскурсии',
                                                     callback_data='user_excursion_info')
        keyboard.add(callback_button_yes, callback_button_back)
        users_cache_dict[call.message.chat.id] = UserCache(datetime.now())
        users_cache_dict[call.message.chat.id].excursion_name = excursion_info[0]
        text = ''
        text += excursion_info[0] + '\n'
        text += excursion_info[1] + '\n'
        text += 'Длительность: ' + excursion_info[2] + 'мин.\n'
        # text += "На данный момент можно записаться на следующие даты: 👇"
        text += 'Заинтересованы?'
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)

    # по нажатию на конкретную дату продолжаем ветку через register_next_step_handler, уточняем детали
    elif call.data.startswith('user_date_choice'):

        # logger.debug(f'{call.from_user.username} from {call.message.chat.id} chose a date (id {call.data.split(".")[1]})')

        # users_cache_dict[call.message.chat.id].window_id = int(call.data.split('.')[1])

        text = 'Как вас записать? (укажите имя)'
        bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(call.message, how_many)


@bot.message_handler(content_types=['text'])
def how_many(message: Message):

    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "how many"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)

    users_cache_dict[message.chat.id].contact_name = message.text
    users_cache_dict[message.chat.id].contact_link = message.from_user.username

    logger.debug(f'{message.from_user.username} from {message.chat.id} named as {message.text}')

    text = "Сколько вас?"
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, confirm_new_visit)


@bot.message_handler(content_types=['text'])
def confirm_new_visit(message: Message):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "confirm_new_visit"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    info = [users_cache_dict[message.chat.id].contact_link, users_cache_dict[message.chat.id].contact_name, message.text]
    # ожидаемые аргументы: сессия и [window_id, contact_link, contact_name, number]
    # при успехе возвращаем объект окна расписания
    result = add_visit_into_window(info)
    # if result:

    logger.info(f'{message.from_user.username} from {message.chat.id} signed to excursion')

    text = (f'🎉Поздравляю! Вы, {users_cache_dict[message.chat.id].contact_name}, успешно записаны '
            f'на экскурсию {users_cache_dict[message.chat.id].excursion_name}!\n'
            f'Наша команда свяжется с вами в ближайшее время')
    for admin in events_listeners_chat_id_list:
        bot.send_message(admin, f'❗️❗️❗️❗️❗️ @{message.from_user.username} записан на '
                                f'на экскурсию {users_cache_dict[message.chat.id].excursion_name}')
    # else:
    #     text = '❌Возникла ошибка! Попробуйте заново или обратитесь к администратору '
    bot.send_message(message.chat.id, text=text)


@bot.callback_query_handler(func=lambda call: 'admin' in call.data)
def admin_functions_entry(call: CallbackQuery):

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} entered admin functions')

    if 'excursion_admin' in call.data:
        if 'add' in call.data:
            text = 'Введите название новой экскурсии'
            bot.send_message(call.message.chat.id, text)
            bot.register_next_step_handler(call.message, new_excursion_ask_description)
            return
        excursion_id = int(call.data.split('.')[1])
        excursion_info_list = get_excursion_info_by_id(excursion_id)
        text = f'Экскурсия: {excursion_info_list[0]}.\n'
        text += f'Описание: {excursion_info_list[1]}\n'
        text += f'Длительность: {excursion_info_list[2]} мин.\n'
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        edit_excursion_btn = types.InlineKeyboardButton(text='Редактировать экскурсию',
                                                        callback_data=f'edit_excursion.{excursion_id}')
        del_excursion_btn = types.InlineKeyboardButton(text='Удалить экскурсию',
                                                        callback_data=f'del_excursion.{excursion_id}')
        # add_window_btn = types.InlineKeyboardButton(text='Добавить окно в расписание',
        #                                             callback_data=f'add_window.{excursion_id}')
        keyboard.add(edit_excursion_btn, del_excursion_btn)
        bot.send_message(call.message.chat.id, text, reply_markup=keyboard)
    elif 'window_admin' in call.data:
        window_id = int(call.data.split('.')[1])
        # -> [title, description, duration, date_time, contact_link, contact_name, visitors]
        window_info = get_window_info_by_id(window_id)
        text = f'{window_info[0]}\n'
        text += f'Описание. {window_info[1]}\n'
        text += f'Длительность {window_info[2]} мин.\n'
        text += f'{window_info[3].strftime("%d.%m.%Y %H:%M")}\n'
        if window_info[4]:
            text += f'Ссылка: {window_info[4]}\n'
            text += f'{window_info[5]}\n'
            text += f'Количество {window_info[6]}\n'
        keyboard = types.InlineKeyboardMarkup()

        edit_window_btn = types.InlineKeyboardButton(text='Редактировать дату',
                                                        callback_data=f'edit_window.{window_id}')
        del_window_btn = types.InlineKeyboardButton(text='Удалить назначенную экскурсию',
                                                     callback_data=f'del_window.{window_id}')
        keyboard.add(edit_window_btn, del_window_btn)
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def new_excursion_ask_description(message: Message):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "new_excursion_ask_description"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    temp = [message.text]
    text = 'Введите описание'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, new_excursion_ask_duration, temp)

@bot.message_handler(content_types=['text'])
def new_excursion_ask_duration(message: Message, temp):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "new_excursion_ask_duration"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    temp.append(message.text)
    text = 'Введите длительность (только число)'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, new_excursion_final, temp)

@bot.message_handler(content_types=['text'])
def new_excursion_final(message: Message, temp):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "new_excursion_final"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    temp.append(message.text)
    res = add_excursion(temp)
    if res:
        logger.info(f'{message.from_user.username} from {message.chat.id} added {temp[0]}')
        bot.send_message(message.chat.id, 'Успешно добавлено')
    else:
        bot.send_message(message.chat.id, 'Произошла ошибка')


@bot.callback_query_handler(func=lambda call: 'edit_excursion' in call.data)
def edit_excursion_question(call: CallbackQuery):
    topic, excursion_id = call.data.split('.')
    excursion_id = int(excursion_id)

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to edit excursion')

    if topic == 'edit_excursion':
        text = 'Что вы хотите поменять?'
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        title_excursion_btn = types.InlineKeyboardButton(text='Название',
                                                        callback_data=f'edit_excursion_title.{excursion_id}')
        description_excursion_btn = types.InlineKeyboardButton(text='Описание',
                                                       callback_data=f'edit_excursion_description.{excursion_id}')
        duration_excursion_btn = types.InlineKeyboardButton(text='Длительность',
                                                    callback_data=f'edit_excursion_duration.{excursion_id}')
        keyboard.add(title_excursion_btn, description_excursion_btn, duration_excursion_btn)
        bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=keyboard)
    elif topic == 'edit_excursion_title':
        text = 'Введите новое название:'
        bot.send_message(call.message.chat.id, text=text)
        bot.register_next_step_handler(call.message, edit_excursion_finish, 'title', excursion_id)
    elif topic == 'edit_excursion_description':
        text = 'Введите новое описание:'
        bot.send_message(call.message.chat.id, text=text)
        bot.register_next_step_handler(call.message, edit_excursion_finish, 'description', excursion_id)
    elif topic == 'edit_excursion_duration':
        text = 'Введите новую длительность в минутах (только число):'
        bot.send_message(call.message.chat.id, text=text)
        bot.register_next_step_handler(call.message, edit_excursion_finish, 'duration', excursion_id)


@bot.message_handler(content_types=['text'])
def edit_excursion_finish(message: Message, attribute_type, excursion_id):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "edit_excursion_finish"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    res = update_excursion_by_id(excursion_id, attribute_type, message)
    if res:
        logger.info(f'{message.from_user.username} from {message.chat.id} updated '
                    f'excursion info with {attribute_type}: {message.text[:25]}')
        bot.send_message(message.chat.id, text='Значение обновлено')
    else:
        bot.send_message(message.chat.id, text='Ошибка')


@bot.callback_query_handler(func=lambda call: 'del_excursion' in call.data)
def del_excursion_question(call: CallbackQuery):

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to delete excursion')

    excursion_id = call.data.split('.')[1]
    keyboard = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text='Да', callback_data=f'yes_del_e.{excursion_id}')
    no_btn = types.InlineKeyboardButton(text='Нет', callback_data=f'no_del_e.{excursion_id}')
    keyboard.add(yes_btn, no_btn)
    bot.send_message(call.message.chat.id, 'Вы уверены?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'yes_del_e' in call.data or 'no_del_e' in call.data)
def del_excursion_confirm(call: CallbackQuery):
    if 'yes' in call.data:
        excursion_id = call.data.split('.')[1]
        res = del_excursion(excursion_id)
        if res:

            logger.info(f'{call.from_user.username} from {call.message.chat.id} deleted an excursion {excursion_id}')

            bot.send_message(call.message.chat.id, 'Экскурсия удалена')
        else:
            bot.send_message(call.message.chat.id, 'Возникла ошибка')
    else:
        bot.send_message(call.message.chat.id, 'Удаление отменено')


@bot.callback_query_handler(func=lambda call: 'add_window' in call.data)
def adding_new_window_question(call: CallbackQuery):

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to add a window')

    excursion_id = call.data.split('.')[1]
    bot.send_message(call.message.chat.id, 'Введите дату в формате дд.мм.гггг чч:мм')
    bot.register_next_step_handler(call.message, adding_new_window_final, excursion_id)

@bot.message_handler(content_types=['text'])
def adding_new_window_final(message: Message, excursion_id):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "adding_new_window_final"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    if (t := check_date(message.text)) != 'ok':

        logger.debug(f'{message.from_user.username} from {message.chat.id} input incorrect date {message.text}')

        bot.send_message(message.chat.id, t)
        return
    res = add_window(excursion_id, message.text)
    if res:

        logger.info(f'{message.from_user.username} from {message.chat.id} added a new window at {message.text} ')

        bot.send_message(message.chat.id, 'Успешно добавлено новое "окошко"!')
    else:
        bot.send_message(message.chat.id, 'Возникла ошибка!')

@bot.callback_query_handler(func=lambda call: 'edit_window' in call.data)
def edit_window_date_question(call: CallbackQuery):

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to edit a window date')

    topic, window_id = call.data.split('.')
    window_id = int(window_id)
    text = 'Введите новую дату:'
    bot.send_message(call.message.chat.id, text=text)
    bot.register_next_step_handler(call.message, edit_window_date_finish, 'date', window_id)


@bot.message_handler(content_types=['text'])
def edit_window_date_finish(message: Message, attribute_type, window_id):
    if message.text in menu_buttons_text:

        logger.debug(f'{message.from_user.username} from {message.chat.id} broke dialog chain before "edit_window_date_finish"')

        text = 'Осуществляю возврат в стартовое меню. Процесс записи будет сброшен.'
        bot.send_message(message.chat.id, text)
        return work(message)
    if (t := check_date(message.text)) != 'ok':

        logger.debug(f'{message.from_user.username} from {message.chat.id} input incorrect date {message.text}')

        bot.send_message(message.chat.id, t)
        return
    res = update_window_by_id(window_id, attribute_type, message)
    if res:

        logger.info(f'{message.from_user.username} from {message.chat.id} update a date:{message.text} ')

        bot.send_message(message.chat.id, text='Дата обновлена')
    else:
        bot.send_message(message.chat.id, text='Ошибка')

@bot.callback_query_handler(func=lambda call: 'del_window' in call.data)
def del_window_question(call: CallbackQuery):

    logger.debug(f'{call.from_user.username} from {call.message.chat.id} wants to del a window')

    window_id = int(call.message.text.split('.')[1])
    keyboard = types.InlineKeyboardMarkup()
    yes_btn = types.InlineKeyboardButton(text='Да', callback_data=f'yes_del_w.{window_id}')
    no_btn = types.InlineKeyboardButton(text='Нет', callback_data=f'no_del_w.{window_id}')
    keyboard.add(yes_btn, no_btn)
    bot.send_message(call.message.chat.id, 'Вы уверены?', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: 'yes_del_w' in call.data or 'no_del_w' in call.data)
def del_window_confirm(call: CallbackQuery):
    if 'yes' in call.data:
        window_id = call.data.split('.')[1]
        res = delete_window(window_id)
        if res:

            logger.info(f'{call.from_user.username} from {call.message.chat.id} deleted a window {window_id}')

            bot.send_message(call.message.chat.id, 'Экскурсия удалена')
        else:

            logger.warn(f'{call.from_user.username} from {call.message.chat.id} tried to del a window {window_id}')

            bot.send_message(call.message.chat.id, 'Возникла ошибка')
    else:
        bot.send_message(call.message.chat.id, 'Удаление отменено')

@bot.callback_query_handler(func=lambda call: 'event' in call.data)
def user_choosing_excursion_window(call):
    answer = call.data.split('.')[1]
    # print(call.from_user, call.message, call.chat_instance, sep='\n')
    logger.info(f'{call.from_user.username} from {call.message.chat.id} switched his events listener status')
    if answer == 'yes':
        text = 'Поздравляю! Теперь вы подписаны на события!'
        events_listeners_chat_id_list.append(call.message.chat.id)
    else:
        text = 'Поздравляю! Теперь вы отписаны от событий!'
        events_listeners_chat_id_list.remove(call.message.chat.id)

    invert_event_listener_status(admins_dict[call.from_user.id])
    bot.send_message(call.message.chat.id, text)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as _ex:
        print(_ex)
        sleep(15)