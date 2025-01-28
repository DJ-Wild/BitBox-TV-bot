import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import time

bot = telebot.TeleBot("7602505753:AAFaYOCHxdakKTbVi4aAxl3wginXwD4p1GA")

moder = 1534688019  # Указал себя для отправки сообщений

# Словарь для отслеживания состояния пользователей
user_states = {}
authenticated_users = set()  # Множество для хранения ID пользователей, успешно прошедших аутентификацию

# Главная клавиатура
mainBut = InlineKeyboardMarkup()
mainBut.add(InlineKeyboardButton("Подписчик", callback_data="sub"))
mainBut.add(InlineKeyboardButton("Корреспондент", callback_data="kor"))  # Создал кнопки

# Клавиатура для подписчиков
subBut = InlineKeyboardMarkup()
subBut.add(InlineKeyboardButton("Сообщить новость", callback_data="news"))
subBut.add(InlineKeyboardButton("Отправить фото", callback_data="photo"))
web_app = WebAppInfo(url="https://dj-wild.github.io/BitBox-TV/")
subBut.add(InlineKeyboardButton("Посетить сайт", web_app=web_app))
subBut.add(InlineKeyboardButton("Написать менеджеру", url="t.me/meneger_BBTV"))
subBut.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

# Клавиатура для корреспондентов
korBut = InlineKeyboardMarkup()
korBut.add(InlineKeyboardButton("Сообщить новость", callback_data="news"))
korBut.add(InlineKeyboardButton("Отправить фото", callback_data="photo"))
korBut.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

exitt = InlineKeyboardMarkup()
exitt.add(InlineKeyboardButton("Назад", callback_data="back_to_main"))

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id  # Для отправки человеку
    bot.send_message(chat_id, f'Приветствуем вас путник! Для начала кто вы?', reply_markup=mainBut)


@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    chat_id = callback.message.chat.id

    if callback.data == 'sub':
        bot.send_message(moder, f"#Зашел @{callback.from_user.username}")
        bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)

    elif callback.data == 'kor':
        if chat_id in authenticated_users:
            # Если пользователь уже аутентифицирован
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            bot.send_message(chat_id, "Вы уже аутентифицированы. Выберите действие.", reply_markup=korBut)
        else:
            bot.delete_message(callback.message.chat.id, callback.message.message_id)
            bot.send_message(chat_id, "Введите пароль", reply_markup=exitt)
            user_states[chat_id] = 'waiting_for_password'  # Устанавливаем состояние пользователя

    elif callback.data == 'photo':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(chat_id, "Отправьте фото, и мы его получим.", reply_markup=exitt)
        user_states[chat_id] = 'waiting_for_photo'  # Устанавливаем состояние для приёма фото

    elif callback.data == 'news':
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(chat_id, "Напишите новость, и мы её отправим модератору.", reply_markup=exitt)
        user_states[chat_id] = 'waiting_for_news'  # Устанавливаем состояние для написания новости

    elif callback.data == 'back_to_main':
        # Возвращаемся на главную клавиатуру
        bot.delete_message(callback.message.chat.id, callback.message.message_id)
        bot.send_message(chat_id, "Вы вернулись на главный экран. Кто вы?", reply_markup=mainBut)
        user_states.pop(chat_id, None)  # Убираем состояние, если оно было


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id

    if user_states.get(chat_id) == 'waiting_for_photo':
        # Получаем файл фото
        file_id = message.photo[-1].file_id
        # Отправляем уведомление модератору
        bot.send_message(moder, f"Пользователь @{message.from_user.username} отправил фото.")
        bot.send_photo(moder, file_id)  # Пересылаем фото модератору

        # Подтверждаем получение пользователю
        bot.send_message(chat_id, "Фото получено. Спасибо!")
        user_states.pop(chat_id, None)  # Убираем состояние
        bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)
    else:
        bot.send_message(chat_id, "Я не ожидал от вас фото. Используйте команду /start, чтобы начать.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if user_states.get(chat_id) == 'waiting_for_password':
        if message.text == "битбоксим":  # Замените на свой пароль
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(chat_id, "Отлично! Выберите действие.", reply_markup=korBut)
            authenticated_users.add(chat_id)  # Добавляем пользователя в список аутентифицированных
            user_states.pop(chat_id, None)  # Убираем состояние
        else:
            bot.send_message(chat_id, "Неверный пароль. Попробуйте ещё раз.")

    elif user_states.get(chat_id) == 'waiting_for_news':
        # Отправляем новость модератору
        bot.send_message(moder, f"Пользователь @{message.from_user.username} отправил новость: {message.text}")

        # Подтверждаем получение пользователю
        bot.send_message(chat_id, "Спасибо! Ваша новость отправлена модератору.")
        user_states.pop(chat_id, None)  # Убираем состояние
        bot.send_message(chat_id, "Зачем же вы пришли сюда?", reply_markup=subBut)

    else:
        bot.send_message(chat_id, "Я не понимаю ваш запрос. Используйте команду /start, чтобы начать.")


# Обёртка для безопасного запуска бота
def run_bot():
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(15)  # Задержка перед повторным запуском


run_bot()
