import telebot
from telebot import types # для указание типов
from db_data import db_functions
name_tg = '@hist_museum_bot'
API_TOKEN = "frgfdhgdf"
bot = telebot.TeleBot(API_TOKEN)
session = db_functions.database_init()


@bot.message_handler(content_types=['text'])
def say_hello(message):
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Моё имя")
        btn2 = types.KeyboardButton("О музее")
        btn3 = types.KeyboardButton("Наш актив")
        btn4 = types.KeyboardButton("Выставки")
        btn5 = types.KeyboardButton("Запись на экскурсию")
        markup.add(btn1, btn2, btn3, btn4, btn5)
        text = 'Привет! 👋 Я - Клио! Я интерактивный помощник Исторического музея школы №13. Задай мне вопрос'
        bot.send_message(message.chat.id, text=text, reply_markup=markup)

    elif (message.text == "Моё имя"):
        bot.send_message(message.chat.id, "Имя Клио я получил в честь музы истории в древнегреческой мифологии.")

    elif (message.text == "О музее"):
        bot.send_message(message.chat.id, "Исторический музей школы №13 создан в 2021 году. Номер свидетельства …… Музей имеет официальный статус и зарегистрирован на портале Школьных музеев. Наш музей совсем молодой, поэтому оживление памяти в формате интерактивных опросов, креативных обзоров и  увлекательных экскурсий - это про нас!")

    elif (message.text == "Наш актив"):
        bot.send_message(message.chat.id, "Наш музейный актив - увлеченные, заинтересованные ребята! Знакомьтесь! Бекетова Влада, Иващенко Лиза, Мосина Вика, Кондрашов Паша, Бессуднов Артём, Коцебук Настя, Синица Лера, Арсений - экскурсоводы и активисты музея.")

    elif (message.text == "Выставки"):
        bot.send_message(message.chat.id, "У нас есть экспозиции, которые мы развиваем и которыми гордимся!  «Калужский край - душа России»,  «Ничто не забыто, никто не забыт», «История школы»")

    elif (message.text == "Запись на экскурсию"):
        info = db_functions.get_current_windows(session)
        text = 'Вот доступные экскурсии\n'
        text += info
        text += '\nУкажите номер'
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, who_are_you, info)

    elif (message.text == "Секрет"):
        bot.send_message(message.chat.id, text='Привет Администратор!')
        bot.register_next_step_handler(message, admin_panel)
    else:
        bot.send_message(message.chat.id, "Я Вас не понимаю. Попробуйте ещё раз.")


@bot.message_handler(content_types=['text'])
def who_are_you(message, info):
    try:
        n = int(message.text.strip())
    except Exception:
        print('Error this is not number!')
    except n <= len(info):
        print('Wrong number')
    else:
        text = "как вас записать?"
        bot.send_message(message.chat.id, text)
        info.append(n)
        bot.register_next_step_handler(message, how_many, info)


@bot.message_handler(content_types=['text'])
def how_many(message, info):
    text = "сколько вас?"
    info.append(message.text)
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, result, info)


@bot.message_handler(content_types=['text'])
def result(message, info):
    try:
        pass
    except:
        pass
    else:
        bot.send_message(message.chat.id, text='ура вы записаны!')

@bot.message_handler(content_types=['text'])
def admin_panel(message):
    print(123213123)
# для админов:
#     1. выводить таблицу текущих экскурсий (название дата кто записан кол-во)
#     2. добавлять окошки
#     3. удалять окошки




bot.infinity_polling()