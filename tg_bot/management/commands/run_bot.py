from django.core.management.base import BaseCommand
from loguru import logger
from tg_bot.initial import bot

import tg_bot.handlers
import tg_bot.signals

import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("🚀 Запуск Telegram бота...")

        while True:
            try:
                bot.infinity_polling(skip_pending=True)
            except Exception as e:
                logger.exception(e)
                time.sleep(5)