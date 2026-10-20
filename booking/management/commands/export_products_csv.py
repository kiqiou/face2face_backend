# booking/management/commands/export_products_csv.py
import csv
from django.core.management.base import BaseCommand
from booking.models import Product


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('out_csv')

    def handle(self, *a, **o):
        with open(o['out_csv'], 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'manufacturer', 'name', 'image_url'])
            qs = Product.objects.filter(media__isnull=True).select_related('manufacturer').order_by('manufacturer__name', 'id')
            for p in qs:
                w.writerow([p.id, p.manufacturer.name, p.name, ''])