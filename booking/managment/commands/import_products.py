import csv
from django.core.management.base import BaseCommand
from booking.models import Product, Manufacturer

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)

    def handle(self, *args, **kwargs):
        with open(kwargs['csv_path'], encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                manufacturer, _ = Manufacturer.objects.get_or_create(name=row['manufacturer'])
                Product.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'description': row['description'],
                        'price_amount': row['price'],
                        'price_currency': row.get('currency', 'BYN'),
                        'manufacturer': manufacturer,
                    }
                )