from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import datetime
from django.core.validators import RegexValidator

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(r'^\+375\d{9}$', message='Неверный формат номера (+375XXXXXXXXX)')])

    def is_cosmetologist(self):
        return self.role and self.role.name == 'cosmetologist'

    def is_client(self):
        return self.role and self.role.name == 'client'

class PhoneVerificationCode(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return self.created_at + datetime.timedelta(minutes=10) < timezone.now()
