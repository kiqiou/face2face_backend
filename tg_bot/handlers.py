from loguru import logger
from telebot import types
from django.core.cache import cache

from tg_bot.initial import bot

import random
from django.core.cache import cache
from loguru import logger
from telebot import types
from tg_bot.initial import bot

@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    args = message.text.split()

    chat_id = message.chat.id

    if len(args) == 1:
        bot.send_message(
            chat_id,
            "👋 Привет!\n\n"
            "Чтобы авторизоваться — перейди по ссылке с сайта."
        )
        return

    token = args[1]
 
    data = cache.get(f"auth_pending:{token}")

    if not data:
        bot.send_message(chat_id, "Ссылка устарела")
        return

    code = str(random.randint(100000, 999999))
    phone = data

    cache.set(f"tg_code:{phone}", code, 300)
    cache.set(f"tg_chat:{phone}", chat_id, 86400 * 30)

    logger.info(f"Code {code} for phone {phone}")
    print(f"Code {code} for phone {phone}")

    bot.send_message(
        chat_id,
        f"🔐 <b>Код подтверждения</b>\n\n"
        f"<code>{code}</code>\n\n"
        f"Введите этот код на сайте",
        parse_mode="HTML"
    )

async def get_auth_token_by_chat(chat_id: int) -> str | None:
    tokens = cache.keys("auth:*")
    for token_key in tokens:
        if cache.get(token_key) == chat_id:
            token = token_key.replace("auth:", "")
            cache.delete(token_key)
            return token
    return None

