from django.conf import settings
from telebot import TeleBot
from telebot.types import BotCommand

bot = TeleBot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")

commands = [
    BotCommand("start", "🚀 Авторизация и управление записями"),
]
bot.set_my_commands(commands)