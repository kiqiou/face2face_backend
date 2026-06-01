from datetime import timedelta

from django.db import models
from users.models import User

class Cosmetologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cosmetologist_profile')
    bio = models.TextField(blank=True)
    specializations = models.CharField(max_length=255, blank=True)
    avatar_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"

class Category(models.Model):
    name = models.CharField(max_length=100, null=False)

class Procedure(models.Model):
    name = models.CharField(max_length=100, null=False)
    price = models.IntegerField(null=False)
    duration = models.DurationField(null=False)  
    description = models.TextField(blank=True)
    buffer_time = models.DurationField(default=timedelta(minutes=10))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='prodecure', null=True)
    cosmetologist = models.ForeignKey(Cosmetologist, on_delete=models.CASCADE, related_name='procedures')

    def __str__(self):
        return f"{self.name} ({self.cosmetologist})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cosmetologist = models.ForeignKey(Cosmetologist, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    procedures = models.ManyToManyField(Procedure)
    duration = models.DurationField()
    price = models.IntegerField()
    status = models.BooleanField(default=True)

class WorkDay(models.Model):
    cosmetologist = models.ForeignKey(
        Cosmetologist,
        on_delete=models.CASCADE,
        related_name='work_days'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_working = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.cosmetologist} {self.date}'
