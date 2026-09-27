from django.core.cache import cache
from loguru import logger
from telebot import types
from tg_bot.initial import bot


@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    args = message.text.split()
    chat_id = message.chat.id

    if len(args) == 1:
        bot.send_message(chat_id, "👋 Привет! Перейди по ссылке с сайта, чтобы авторизоваться.")
        return

    token = args[1]

    if not cache.get(f"auth_pending:{token}"):
        bot.send_message(chat_id, "Ссылка устарела, вернитесь на сайт и попробуйте снова.")
        return

    # прямая связка в обе стороны — без сканирования ключей
    cache.set(f"auth_chat_to_token:{chat_id}", token, 300)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("📱 Поделиться номером телефона", request_contact=True))

    bot.send_message(
        chat_id,
        "Нажмите кнопку ниже, чтобы подтвердить номер и войти на сайте.",
        reply_markup=keyboard,
    )


@bot.message_handler(content_types=["contact"])
def handle_contact(message: types.Message):
    chat_id = message.chat.id
    contact = message.contact

    if contact.user_id != message.from_user.id:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку ниже, а не пересылайте контакт вручную.")
        return

    token = cache.get(f"auth_chat_to_token:{chat_id}")

    if not token:
        bot.send_message(chat_id, "Сессия авторизации не найдена, начните заново с сайта.")
        return

    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    cache.set(f"auth_result:{token}", {"phone": phone, "chat_id": chat_id}, 300)
    cache.delete(f"auth_pending:{token}")
    cache.delete(f"auth_chat_to_token:{chat_id}")

    logger.info(f"Telegram auth confirmed: token={token} chat_id={chat_id}")
    bot.send_message(chat_id, "✅ Готово! Вернитесь на сайт — вход выполнится автоматически.", reply_markup=types.ReplyKeyboardRemove())