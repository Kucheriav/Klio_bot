import telebot
from telebot import types # для указание типов
from db_data import db_models, db_functions
name_tg = '@hist_museum_bot'
API_TOKEN = "rtytryrty"
bot = telebot.TeleBot(API_TOKEN)
db_functions.database_init()






@bot.message_handler(content_types=['text'])
def say_hello(message):
    if message.text == '/start':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("один")
        btn2 = types.KeyboardButton("два")
        btn3 = types.KeyboardButton("три")
        btn4 = types.KeyboardButton("xtns")
        btn5 = types.KeyboardButton("gznm")
        markup.add(btn1, btn2, btn3,btn4, btn5)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)
        #bot.send_message(message.from_user.id, 'Привет! 👋 Я - Клио! Я интерактивный помощник Исторического музея школы №13')

    elif (message.text == "один"):
        bot.send_message(message.chat.id, "У меня нет имени..")

    else:
        pass

bot.infinity_polling()