from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class User(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    personal_data_consent_at = models.DateTimeField(null=True, blank=True)
    personal_data_consent_ip = models.GenericIPAddressField(null=True, blank=True)
    manual_discount_percent = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text="Скидка, выставленная вручную — если задана, имеет приоритет над автоматической"
    )
    phone = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^\+375\d{9}$', message='Неверный формат номера (+375XXXXXXXXX)')]
    )