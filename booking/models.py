from django.db import models
from users.models import User

class Cosmetologist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cosmetologist_profile')
    bio = models.TextField(blank=True)
    specializations = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.user.username}"

class Procedure(models.Model):
    name = models.CharField(max_length=100, null=False)
    price = models.IntegerField(null=False)
    duration = models.DurationField(null=False)  
    cosmetologist = models.ForeignKey(Cosmetologist, on_delete=models.CASCADE, related_name='procedures')

    def __str__(self):
        return f"{self.name} ({self.cosmetologist})"

class Appointment(models.Model):
    date = models.DateField(null=False)
    time = models.TimeField(null=False)
    cosmetologist = models.ForeignKey(Cosmetologist, on_delete=models.CASCADE, related_name='appointments')
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} {self.time} | {self.procedure.name}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='bookings')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='bookings')
    status = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.username} - {self.appointment}'

