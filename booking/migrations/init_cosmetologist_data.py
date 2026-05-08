from django.db import migrations
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import re


def create_initial_data(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    User = apps.get_model('users', 'User')
    Cosmetologist = apps.get_model('booking', 'Cosmetologist')
    Procedure = apps.get_model('booking', 'Procedure')

    # Роли
    client_role, _ = Role.objects.get_or_create(
        name='client'
    )

    cosmetologist_role, _ = Role.objects.get_or_create(
        name='cosmetologist'
    )

    # Вера
    vera_user, _ = User.objects.get_or_create(
        username='vera_kuksar',
        defaults={
            'first_name': 'Вера',
            'last_name': 'Куксар',
            'email': 'vera@example.com',
            'phone': '+375447799393',
            'role': cosmetologist_role,
            'password': make_password('111111Aa!'),
            'is_active': True,
            'is_staff': True,
        }
    )

    vera_cosm, _ = Cosmetologist.objects.get_or_create(
        user=vera_user,
        defaults={
            'bio': 'Мой конёк - естественные брови...',
            'specializations': 'Косметик',
            'avatar_url': 'https://res.cloudinary.com/dpaq2o0di/image/upload/v1775289466/kuksar_vera_q4jfxr.jpg'
        }
    )

    # Анастасия
    ana_user, _ = User.objects.get_or_create(
        username='anastasia',
        defaults={
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

    ana_cosm, _ = Cosmetologist.objects.get_or_create(
        user=ana_user,
        defaults={
            'bio': '-',
            'specializations': 'Косметик',
            'avatar_url': 'https://res.cloudinary.com/dpaq2o0di/image/upload/v1775289466/anastasia_ogrdd3.jpg'
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

    # Процедуры Веры
    vera_procs = [
        ("Hydra active", 85, "1ч"),
        ("Snow white", 85, "1ч"),
    ]

    for name, price, dur in vera_procs:
        Procedure.objects.get_or_create(
            cosmetologist=vera_cosm,
            name=name,
            defaults={
                'price': price,
                'duration': parse_duration(dur)
            }
        )

    # Процедуры Анастасии
    ana_procs = [
        ("Express-уход GIGI BIOPLASMA", 130, "1ч"),
        ("Карбокситерапия", 120, "1ч"),
    ]

    for name, price, dur in ana_procs:
        Procedure.objects.get_or_create(
            cosmetologist=ana_cosm,
            name=name,
            defaults={
                'price': price,
                'duration': parse_duration(dur)
            }
        )


def reverse_func(apps, schema_editor):
    Procedure = apps.get_model('booking', 'Procedure')
    Cosmetologist = apps.get_model('booking', 'Cosmetologist')
    User = apps.get_model('users', 'User')
    Role = apps.get_model('users', 'Role')

    usernames = ['vera_kuksar', 'anastasia']

    Procedure.objects.filter(
        cosmetologist__user__username__in=usernames
    ).delete()

    Cosmetologist.objects.filter(
        user__username__in=usernames
    ).delete()

    User.objects.filter(
        username__in=usernames
    ).delete()

    Role.objects.filter(
        name__in=['client', 'cosmetologist']
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_telegram_id'),
        ('booking', '0009_delete_timeslot'),
    ]

    operations = [
        migrations.RunPython(create_initial_data, reverse_func),
    ]