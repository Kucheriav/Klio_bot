import telebot
from telebot import types # для указание типов
from db_data.db_functions import *

API_TOKEN = ""
ADMINS = [1756860408, 1672823252, 130612247]
name_tg = '@hist_museum_bot'
bot = telebot.TeleBot(API_TOKEN)
session, _ = database_init()

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
        callback_button = types.InlineKeyboardButton(text="📝Запись на экскурсию", callback_data='zapis')
        keyboard.add(callback_button)
        bot.send_message(message.chat.id,
                         "Записаться на экскурсию можно в кабинете 301 на третьем этаже или нажав на кнопку ниже. Мы всегда рады вас видеть и подберем удобное время!",
                         reply_markup=keyboard)

    elif (message.text == "📝Запись на экскурсию"):
        bot.send_message(message.chat.id,
                         "У нас есть экспозиции, которые мы развиваем и которыми гордимся!  «Калужский край - душа России»,  «Ничто не забыто, никто не забыт», «История школы»")

    # elif (message.text == "Запись на экскурсию"):
    #     info = db_functions.get_current_windows(session)
    #     text = 'Вот доступные экскурсии\n'
    #     text += info
    #     text += '\nУкажите номер'
    #     bot.send_message(message.chat.id, text)
    #     bot.register_next_step_handler(message, who_are_you, info)

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
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global ex
    if call.message:
        if call.data == 'zapis':
            keyboard = types.ReplyKeyboardMarkup()
            windows_names = get_current_windows_names(session)
            print(windows_names)
            # keyboard.add(types.KeyboardButton(callback_data='sa', text=f'hgf❓'))
            for name in windows_names:
                # cleaned_data = re.sub(r'[^a-z0-9_\-]', '', i.strip().lower())
                keyboard.add(types.KeyboardButton(text=f'{name}'))
            bot.send_message(call.message.chat.id, f"На данный момент можно записаться на следующие экскурсии: 👇",
                             reply_markup=keyboard)

            # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="На данный момент можно записаться на следующие экскурсии", reply_markup=markup)

#
# @bot.message_handler(content_types=['text'])
# def who_are_you(message, id_list):
#     try:
#         n = int(message.text.strip())
#     except Exception:
#         print('Error this is not number!')
#     except n >= len(id_list):
#         print('Wrong number')
#     else:
#         text = "как вас записать?"
#         bot.send_message(message.chat.id, text)
#         this_id = id_list[n - 1]
#         bot.register_next_step_handler(message, how_many, this_id)


# @bot.message_handler(content_types=['text'])
# def how_many(message, this_id):
#     visit = [this_id, message.from_user.username, message.text]
#     text = "сколько вас?"
#     bot.send_message(message.chat.id, text)
#     bot.register_next_step_handler(message, result, visit)


# @bot.message_handler(content_types=['text'])
# def result(message, visit):
#     visit.append(message.text)
#     try:
#         db_functions.application_for_visit(session, visit)
#     except:
#         bot.send_message(message.chat.id, text='Ошибка БД. Обратитесь к разработчику')
#     else:
#         bot.send_message(message.chat.id, text='Ура, вы записаны!')

@bot.message_handler(content_types=['text'])
def admin_panel(message):
    print(123213123)
# для админов:
#     1. выводить таблицу текущих экскурсий (название дата кто записан кол-во)
#     2. добавлять окошки
#     3. удалять окошки




def get_windows_info(info):
    res = ''
    for variant in info:
        res += f'{variant[1]}. {variant[2]} \n'
        res += f'{variant[3]}\n'
        res += f'Длительность: {variant[4]} минут.'
        res += '---------------\n'
    return res




bot.infinity_polling()