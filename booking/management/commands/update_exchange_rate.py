
import requests
from django.core.management.base import BaseCommand
from booking.models import ExchangeRate

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        resp = requests.get('https://api.nbrb.by/exrates/rates/431')  # 431 = USD
        data = resp.json()
        ExchangeRate.objects.update_or_create(
            currency='USD',
            defaults={'rate_to_byn': data['Cur_OfficialRate']}
        )