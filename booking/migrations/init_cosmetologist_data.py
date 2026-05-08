from django.db import migrations
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import re

def create_initial_data(apps, schema_editor):
    # Получаем модели
    Role = apps.get_model('users', 'Role')
    User = apps.get_model('users', 'User')
    Cosmetologist = apps.get_model('booking', 'Cosmetologist')
    Procedure = apps.get_model('booking', 'Procedure')
    
    # Создаем роли
    Role.objects.get_or_create(id=1, defaults={'name': 'client'})
    Role.objects.get_or_create(id=2, defaults={'name': 'cosmetologist'})
    
    client_role = Role.objects.get(id=1)
    cosmetologist_role = Role.objects.get(id=2)
    
    # Вера (id=37)
    vera_user, _ = User.objects.get_or_create(
        id=37,
        defaults={
            'username': 'vera_kuksar',
            'first_name': 'Вера',
            'last_name': 'Куксар',
            'email': 'vera@example.com',
            'phone': '+375447799393',  # Реальный номер
            'role': cosmetologist_role,
            'password': make_password('111111Aa!'),
            'is_active': True,
            'is_staff': True,
        }
    )
    Cosmetologist.objects.get_or_create(
        user=vera_user,
        defaults={
            'bio': "Мой конёк - естественные брови. Я не рисую «одну бровь на всех», а создаю изгиб, который идеально повторит вашу анатомию и сделает взгляд выразительным. С помощью ламинирования я создаю красивый, естественный изгиб ресниц, который открывает взгляд и сохраняет свою форму. Имея диплом косметика 5-го разряда, я не только работаю с формой, но и учу заботиться о содержании. Помогаю вашей коже быть здоровой, сияющей и ухоженной с помощью грамотного домашнего и профессионального ухода.",
            'specializations': "Косметик",
            'avatar_url': "https://res.cloudinary.com/dpaq2o0di/image/upload/v1775289466/kuksar_vera_q4jfxr.jpg"
        }
    )
    
    # Анастасия (id=38)
    ana_user, _ = User.objects.get_or_create(
        id=38,
        defaults={
            'username': 'anastasia',
            'first_name': 'Анастасия',
            'last_name': '',
            'email': 'anastasia@example.com',
            'phone': '+375291786034',
            'role': cosmetologist_role,
            'password': make_password('111111Aa!'),
            'is_active': True,
            'is_staff': True,
        }
    )
    Cosmetologist.objects.get_or_create(
        user=ana_user,
        defaults={
            'bio': "-",
            'specializations': "Косметик",
            'avatar_url': "https://res.cloudinary.com/dpaq2o0di/image/upload/v1775289466/anastasia_ogrdd3.jpg"
        }
    )
    
    # Парсер длительности
    def parse_duration(dur_str):
        dur_str = re.sub(r'[^\dчмин\s]', '', dur_str.lower())
        hours_match = re.search(r'(\d+)\s*ч', dur_str)
        mins_match = re.search(r'(\d+)\s*мин', dur_str)
        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(mins_match.group(1)) if mins_match else 0
        return timedelta(hours=hours, minutes=minutes)
    
    # Процедуры Веры (cosmetologist_id=37)
    vera_procs = [
        ("Hydra active", 85, "1ч"),
        ("Snow white", 85, "1ч"),
        ("Vitc + gsh", 85, "1ч"),
        ("УЗ чистка + массаж", 59, "1ч 20мин"),
        ("УЗ чистка антивозрастной пилинг", 80, "1ч 20мин"),
        ("УЗ чистка антиоксидантный пилинг", 80, "1ч 20мин"),
        ("УЗ чистка, пилинг для жирной кожи", 75, "1ч 20мин"),
        ("УЗ чистка, пилинг для чувствительной кожи", 75, "1ч 20мин"),
        ("Массаж, антивозрастной пилинг", 80, "1ч"),
        ("Массаж антиоксидантный пилинг", 80, "1ч"),
        ("Массаж, пилинг для жирной кожи", 75, "1ч"),
        ("Массаж пилинг для чувствительной кожи", 75, "1ч"),
        ("Долговременная укладка бровей", 50, "1ч"),
        ("Комплекс ламинирование ресниц и оформление бровей", 80, "1ч 40мин"),
        ("Коррекция и окрашивание бровей", 40, "50мин"),
        ("Ламинирование ресниц", 50, "20мин"),  # 5бун -> 50?
        ("Массаж лица: миофасциальный + лимфодренад", 60, "1ч"),  # Цена предположена
]
    
    for name, price, dur in vera_procs:
        Procedure.objects.get_or_create(
            cosmetologist_id=37,
            name=name,
            defaults={'price': price, 'duration': parse_duration(dur)}
        )
    
    # Процедуры Анастасии (cosmetologist_id=38)
    ana_procs = [
        ("Express-уход GIGI BIOPLASMA", 130, "1ч"),
        ("Relax уход (вкл. руки, декольте + пилинг)", 110, "1ч 30мин"),  # Цена предположена
        ("Банкетный уход: карбокситерапия Премиум + альгинатная маска", 110, "1ч 30мин"),
        ("Карбокситерапия", 120, "1ч"),
        ("Уход по типу кожи без массажа", 95, "1ч"),
        ("Уход по типу кожи с массажем", 110, "1ч 30мин"),
        ("Фракционная мезотерапия + пилинг PRTX (лицо)", 150, "1ч 30мин"),
        ("Фракционная мезотерапия + пилинг PRTX (лицо+шея+декольте)", 170, "1ч 30мин"),
        ("Фракционная мезотерапия + сыворотка (лицо)", 130, "1ч 30мин"),
        ("Фракционная мезотерапия + сыворотка (лицо+шея+декольте)", 140, "1ч 30мин"),
        ("Фракционная мезотерапия + пилинг Biorepeel (лицо)", 140, "2ч"),
        ("Фракционная мезотерапия + пилинг Biorepeel (лицо+шея+декольте)", 160, "1ч 30мин"),
        ("Чистка комбинированная + карбокситерапия ANGIOPHARM", 150, "2ч"),
        ("Чистка комбинированная + карбокситерапия лота", 120, "2ч"),
        ("Чистка комбинированная + пилинг Biorepeel", 150, "2ч"),
        ("Чистка лица комбинированная: УЗ+мех+пилинг", 120, "1ч 30мин"),
        ("Чистка спины + пилинг", 130, "2ч"),
        ("Пилинг Biorepeel", 120, "1ч"),
        ("Пилинг PRXT", 130, "1ч"),
        ("Пилинг поверхностный", 95, "30мин"),
        ("Пилинг поверхностный (лицо+шея+декольте)", 115, "30мин"),
        ("Консультация", 25, "30мин"),
    ]
    
    for name, price, dur in ana_procs:
        Procedure.objects.get_or_create(
            cosmetologist_id=38,
            name=name,
            defaults={'price': price, 'duration': parse_duration(dur)}
        )

def reverse_func(apps, schema_editor):
    Procedure = apps.get_model('booking', 'Procedure')
    Cosmetologist = apps.get_model('booking', 'Cosmetologist')
    User = apps.get_model('users', 'User')
    Role = apps.get_model('users', 'Role')
    
    Procedure.objects.filter(cosmetologist__user__id__in=[37,38]).delete()
    Cosmetologist.objects.filter(user__id__in=[37,38]).delete()
    User.objects.filter(id__in=[37,38]).delete()
    Role.objects.filter(id__in=[1,2]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0004_user_telegram_id'),  # Твоя последняя миграция users
        ('booking', '0009_delete_timeslot'),  # Твоя последняя миграция booking
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_func),
    ]