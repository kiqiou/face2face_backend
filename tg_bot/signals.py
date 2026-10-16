from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from users.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import requests
from booking.models import Order

def get_user_chat_id(user_id: int) -> int | None:
    return cache.get(f"user:{user_id}:chat") or User.objects.filter(id=user_id).values_list('telegram_id', flat=True).first()

@receiver(post_save, sender=Order)
def notify_telegram_on_order(sender, instance, created, **kwargs):
    if not created:
        return

    username = instance.user.username if instance.user else "Гость"
    phone = instance.user.phone if instance.user else "Не указан"

    text = (
        f"🛒 Новый заказ #{instance.id}\n"
        f"Имя: {username}\n"
        f"Телефон: {phone}\n"
        f"Оплата: {instance.get_payment_method_display()}\n"
        f"Подтверждение: {instance.get_approvement_method_display()}"
    )

    requests.post(
        f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
        data={
            'chat_id': settings.ADMIN_TG_CHAT_ID,
            'text': text
        }
    )