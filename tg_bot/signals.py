from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import sync_to_async
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from tg_bot.initial import bot
from booking.models import Booking
from django.core.cache import cache

from users.models import User

@receiver(post_save, sender=Booking)
def booking_notification(sender, instance, created, **kwargs):
    if created:
        send_booking_created(instance)
    else:
        send_booking_updated(instance)

@receiver(post_delete, sender=Booking)
def booking_deleted_notification(sender, instance, **kwargs):
    send_booking_deleted(instance)

def get_user_chat_id(user_id: int) -> int | None:
    return cache.get(f"user:{user_id}:chat") or User.objects.filter(id=user_id).values_list('telegram_id', flat=True).first()

def send_booking_created(booking: Booking):
    user_chat_id = get_user_chat_id(booking.user_id)
    cosmetologist_chat_id = get_user_chat_id(booking.cosmetologist.user.id)
    
    if not user_chat_id and not cosmetologist_chat_id:
        return
    
    procedures = ", ".join([p.name for p in booking.procedures.all()])
    
    message = (
        f"🆕 <b>Новая запись</b>\n\n"
        f"💇‍♀️ Косметолог: {booking.cosmetologist.user.username}\n"
        f"📅 Дата: {booking.date.strftime('%d.%m.%Y')}\n"
        f"🕐 Время: {booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}\n"
        f"⏱️ Длительность: {booking.duration}\n"
        f"💰 Стоимость: {booking.price} BYN\n"
        f"📋 Процедуры: {procedures}\n"
        f"📊 Статус: {'✅ Активна' if booking.status else '❌ Отменена'}"
    )
    
    if user_chat_id:
        bot.send_message(user_chat_id, message, parse_mode="HTML")
    if cosmetologist_chat_id:
        bot.send_message(cosmetologist_chat_id, message, parse_mode="HTML")

def send_booking_updated(booking: Booking):
    user_chat_id = get_user_chat_id(booking.user_id)
    cosmetologist_chat_id = get_user_chat_id(booking.cosmetologist.user.id)
    
    if not user_chat_id and not cosmetologist_chat_id:
        return
    
    message = (
        f"✏️ <b>Запись обновлена</b>\n"
        f"ID: <code>{booking.id}</code>\n"
        f"💰 {booking.price}BYN | {booking.date} {booking.start_time}",
    )
    
    if user_chat_id:
        bot.send_message(user_chat_id, message, parse_mode="HTML")
    if cosmetologist_chat_id:
        bot.send_message(cosmetologist_chat_id, message, parse_mode="HTML")

def send_booking_deleted(booking: Booking):
    chat_id = get_user_chat_id(booking.user_id)
    if not chat_id:
        return
    
    bot.send_message(
        chat_id,
        f"🗑️ <b>Запись отменена</b>\n"
        f"📅 {booking.date} {booking.start_time}\n"
        f"💰 {booking.price}BYN"
    )