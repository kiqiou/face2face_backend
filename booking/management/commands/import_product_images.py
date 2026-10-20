# booking/management/commands/import_product_images.py
import csv, mimetypes, os
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile

from booking.models import Product, ProductMedia


class Command(BaseCommand):
    help = "CSV (id,image_url[,score]) -> загрузка фото в ProductMedia"

    def add_arguments(self, parser):
        parser.add_argument('csv_path')
        parser.add_argument('--dry-run', action='store_true')
        parser.add_argument('--min-score', type=float, default=0,
                            help='пропускать строки, где score ниже порога')

    def handle(self, *args, **opts):
        ok = skipped = failed = 0
        with open(opts['csv_path'], encoding='utf-8-sig', newline='') as f:
            for row in csv.DictReader(f):
                urls = [u.strip() for u in (row.get('image_url') or '').split('|') if u.strip()]
                if not urls:
                    continue
                if float(row.get('score') or 1) < opts['min_score']:
                    skipped += 1
                    continue

                product = Product.objects.filter(id=row['id']).first()
                if not product:
                    self.stderr.write(f"Нет товара id={row['id']}")
                    failed += 1
                    continue
                if product.media.exists():
                    skipped += 1
                    continue

                for order, url in enumerate(urls):
                    try:
                        r = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
                        r.raise_for_status()
                        ctype = r.headers.get('Content-Type', '').split(';')[0]
                        if not ctype.startswith('image'):
                            raise ValueError(f'не картинка: {ctype}')
                        ext = mimetypes.guess_extension(ctype) or os.path.splitext(urlparse(url).path)[1] or '.jpg'
                        if opts['dry_run']:
                            self.stdout.write(f"[dry] {product.id} <- {url}")
                            continue
                        ProductMedia.objects.create(
                            product=product,
                            file=SimpleUploadedFile(
                                f'product_{product.id}_{order}{ext}', r.content, content_type=ctype),
                            media_type='image',
                            order=order,
                        )
                        ok += 1
                    except Exception as e:
                        failed += 1
                        self.stderr.write(f"id={product.id} {url}: {e}")

        self.stdout.write(self.style.SUCCESS(f"Загружено: {ok}, пропущено: {skipped}, ошибок: {failed}"))