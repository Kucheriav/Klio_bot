import telebot
from telebot import types # для указание типов
from db_data.db_functions import *
from users_states import User



API_TOKEN = ""
ADMINS = [1756860408, 1672823252, 130612247]
name_tg = '@hist_museum_bot'
bot = telebot.TeleBot(API_TOKEN)
session, _ = database_init()
users_states = dict()

# из-за многоэтапной процедуры выбора экскурсии нам надо как-то хранить состояние пользователя
# тогда можно сократить кол-во запросов к бд, сразу выдергивая, например, объекты окошек целиком,
# а не бегать за каждый клочком инфы на очередном этапе регистрации на экскурсию

@bot.message_handler(content_types=['text'])
def work(message):
    q = message.chat.id
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("❗Моё имя")
        btn2 = types.KeyboardButton("🏛️О музее")
        markup.add(btn1, btn2)
        btn3 = types.KeyboardButton("ℹ️Выставки")
        btn4 = types.KeyboardButton("🔥Наш актив")
        markup.add(btn3, btn4)
        btn_zap = types.KeyboardButton('❓Как попасть на экскурсию в музей?')
        markup.add(btn_zap)
        if message.from_user.id in ADMINS:
            admbtn = types.KeyboardButton("💻Панель администратора")
            markup.add(admbtn)

        text = 'Привет! 👋 Я - Клио! Я интерактивный помощник Исторического музея школы №13.'
        bot.send_photo(q, open('menu.jpg', 'rb'), caption=text)
        bot.send_message(q, 'Выберите одну из команд в меню: 👇', reply_markup=markup)


    elif (message.text == "❗Моё имя"):
        bot.send_message(message.chat.id, "Имя Клио я получил в честь музы истории в древнегреческой мифологии.")

    elif (message.text == "🏛️О музее"):
        bot.send_message(message.chat.id,
                         "Исторический музей школы №13 создан в 2021 году. Номер свидетельства …… Музей имеет официальный статус и зарегистрирован на портале Школьных музеев. Наш музей совсем молодой, поэтому оживление памяти в формате интерактивных опросов, креативных обзоров и  увлекательных экскурсий - это про нас!")

    elif (message.text == "🔥Наш актив"):
        bot.send_message(message.chat.id,
                         "Наш музейный актив - увлеченные, заинтересованные ребята! Знакомьтесь! Бекетова Влада, Иващенко Лиза, Мосина Вика, Кондрашов Паша, Бессуднов Артём, Коцебук Настя, Синица Лера, Арсений - экскурсоводы и активисты музея.")
    elif message.text == "❓Как попасть на экскурсию в музей?":
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="📝Запись на экскурсию", callback_data='excursion_info')
        keyboard.add(callback_button)
        bot.send_message(message.chat.id,
                         "Записаться на экскурсию можно в кабинете 301 на третьем этаже или нажав на кнопку ниже. Мы всегда рады вас видеть и подберем удобное время!",
                         reply_markup=keyboard)

    # этого же уже нет на клавиатуре? удалить?
    # elif (message.text == "📝Запись на экскурсию"):
    #     bot.send_message(message.chat.id,
    #                      "У нас есть экспозиции, которые мы развиваем и которыми гордимся!  «Калужский край - душа России»,  «Ничто не забыто, никто не забыт», «История школы»")


    elif (message.text == "💻Панель администратора"):

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("📝Расписание")
        btn2 = types.KeyboardButton("🛢Время экскурсий")
        markup.add(btn1, btn2)
        btn3 = types.KeyboardButton("ℹ️Выставки")
        btn4 = types.KeyboardButton("🥃Экскурсии")
        markup.add(btn3, btn4)
        bot.send_message(message.chat.id, text='Привет Администратор!', reply_markup=markup)
    else:
        print(message.text)
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'excursion_info':
            users_states[call.message.chat.id] = User()
            windows_names = sorted(list(get_current_windows_names(session)))
            users_states[call.message.chat.id].actual_excursions = windows_names[:]
            keyboard = types.InlineKeyboardMarkup()
            for i, name in enumerate(windows_names):
                callback_button = types.InlineKeyboardButton(text=name, callback_data=f'excursion_choice.{i}')
                keyboard.add(callback_button)
            bot.send_message(call.message.chat.id, "На данный момент можно записаться на следующие экскурсии: 👇",
                             reply_markup=keyboard)
        elif call.data.startswith('excursion_choice'):
            excursion_choice = users_states[call.message.chat.id].actual_excursions[int(call.data.split('.')[1])]
            users_states[call.message.chat.id].excursion_choice = excursion_choice
            dates = sorted(list(get_actual_dates_by_name(session, excursion_choice)))
            users_states[call.message.chat.id].actual_dates = dates[:]
            keyboard = types.InlineKeyboardMarkup()
            for i, date in enumerate(dates):
                callback_button = types.InlineKeyboardButton(text=date.strftime("%d.%m.%Y"), callback_data=f'date_choice.{i}')
                keyboard.add(callback_button)
            text = ''
            text += excursion_choice + '\n'
            text += get_description_by_title(session, excursion_choice)+ '\n'
            text += "На данный момент можно записаться на следующие даты: 👇"
            bot.send_message(call.message.chat.id, text,
                             reply_markup=keyboard)
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
    # visit_info = [window_id, contact_link, contact_name,  number]
    result = add_visit(session, [window_id, users_states[message.chat.id].contact_link,
                                 users_states[message.chat.id].contact_name, number])

    bot.send_message(message.chat.id, text=result)

@bot.message_handler(content_types=['text'])
def admin_panel(message):
    print(123213123)
# для админов:
#     1. выводить таблицу текущих экскурсий (название дата кто записан кол-во)
#     2. добавлять окошки
#     3. удалять окошки







bot.infinity_polling()