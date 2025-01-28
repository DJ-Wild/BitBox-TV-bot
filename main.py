import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import time

bot = telebot.TeleBot("7665835772:AAHHcoyAM2TvLtqmmCwaqiOU3S4F4Fnw-4s")
moder = 1534688019  # ID модератора
channel_id = "@bebebeFu "  # Укажите username вашего канала

# Словари для отслеживания состояния
user_states = {}
authenticated_users = set()

# Главная клавиатура
mainBut = InlineKeyboardMarkup()
mainBut.add(InlineKeyboardButton("Подписчик", callback_data="sub"))
mainBut.add(InlineKeyboardButton("Корреспондент", callback_data="kor"))

# Клавиатуры
subBut = InlineKeyboardMarkup()
subBut.add(InlineKeyboardButton("Сообщить новость", callback_data="news"))
subBut.add(InlineKeyboardButton("Отправить фото", callback_data="photo"))
web_app = WebAppInfo(url="https://dj-wild.github.io/BitBox-TV/")
subBut.add(InlineKeyboardButton("Посетить сайт", web_app=web_app))
subBut.add(InlineKeyboardButton("Написать менеджеру", url="t.me/meneger_BBTV"))
subBut.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

korBut = InlineKeyboardMarkup()
korBut.add(InlineKeyboardButton("Сообщить новость", callback_data="news"))
korBut.add(InlineKeyboardButton("Отправить фото", callback_data="photo"))
korBut.add(InlineKeyboardButton("Выложить пост", callback_data="post"))
korBut.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

exitt = InlineKeyboardMarkup()
exitt.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f'Приветствуем вас путник! Для начала кто вы?', reply_markup=mainBut)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id = callback.message.chat.id

    if callback.data == 'sub':
        bot.send_message(moder, f"#Зашел @{callback.from_user.username}")
        bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)

    elif callback.data == 'kor':
        if chat_id in authenticated_users:
            bot.delete_message(chat_id, callback.message.message_id)
            bot.send_message(chat_id, "Вы уже аутентифицированы. Выберите действие.", reply_markup=korBut)
        else:
            bot.delete_message(chat_id, callback.message.message_id)
            bot.send_message(chat_id, "Введите пароль", reply_markup=exitt)
            user_states[chat_id] = 'waiting_for_password'

    elif callback.data == 'photo':
        bot.delete_message(chat_id, callback.message.message_id)
        bot.send_message(chat_id, "Отправьте фото, и мы его получим.", reply_markup=exitt)
        user_states[chat_id] = 'waiting_for_photo'

    elif callback.data == 'news':
        bot.delete_message(chat_id, callback.message.message_id)
        bot.send_message(chat_id, "Напишите новость, и мы её отправим модератору.", reply_markup=exitt)
        user_states[chat_id] = 'waiting_for_news'

    elif callback.data == 'post':
        bot.delete_message(chat_id, callback.message.message_id)
        bot.send_message(chat_id, "Отправьте текст поста или фото с подписью для публикации в канал.", reply_markup=exitt)
        user_states[chat_id] = 'waiting_for_post'

    elif callback.data == 'back_to_main':
        bot.delete_message(chat_id, callback.message.message_id)
        bot.send_message(chat_id, "Вы вернулись на главный экран. Кто вы?", reply_markup=mainBut)
        user_states.pop(chat_id, None)


@bot.message_handler(content_types=['photo', 'text'])
def handle_message(message):
    chat_id = message.chat.id

    if user_states.get(chat_id) == 'waiting_for_password':
        if message.text == "битбоксим":
            bot.delete_message(chat_id, message.message_id)
            bot.send_message(chat_id, "Отлично! Выберите действие.", reply_markup=korBut)
            authenticated_users.add(chat_id)
            user_states.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "Неверный пароль. Попробуйте ещё раз.")

    elif user_states.get(chat_id) == 'waiting_for_news':
        bot.send_message(moder, f"Пользователь @{message.from_user.username} отправил новость: {message.text}")
        bot.send_message(chat_id, "Спасибо! Ваша новость отправлена модератору.")
        user_states.pop(chat_id, None)
        bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)

    elif user_states.get(chat_id) == 'waiting_for_photo':
        if message.photo:
            file_id = message.photo[-1].file_id
            bot.send_message(moder, f"Пользователь @{message.from_user.username} отправил фото.")
            bot.send_photo(moder, file_id)
            bot.send_message(chat_id, "Фото получено. Спасибо!")
            user_states.pop(chat_id, None)
            bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)

    elif user_states.get(chat_id) == 'waiting_for_post':
        if message.photo:
            file_id = message.photo[-1].file_id
            caption = message.caption if message.caption else " "
            bot.send_photo(channel_id, file_id, caption=caption)
            bot.send_message(chat_id, "Пост опубликован в канале!")
        elif message.text:
            bot.send_message(channel_id, message.text)
            bot.send_message(chat_id, "Пост опубликован в канале!")
        else:
            bot.send_message(chat_id, "Ошибка: отправьте текст или фото для публикации.")
        user_states.pop(chat_id, None)

    else:
        bot.send_message(chat_id, "Я не понимаю ваш запрос. Используйте команду /start, чтобы начать.")


import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render указывает PORT через переменные окружения
    app.run(host="0.0.0.0", port=port)

def run_bot():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)


run_bot()
