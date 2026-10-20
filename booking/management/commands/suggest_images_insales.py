# booking/management/commands/suggest_images_insales.py
import csv, re, time, html, difflib
from urllib.parse import quote
import requests
from django.core.management.base import BaseCommand
from booking.models import Product

H = {'User-Agent': 'Mozilla/5.0'}
LINK = re.compile(r'<a[^>]+href="([^"]*?/product/[^"#?]+)[^"]*"[^>]*>(.*?)</a>', re.S)
OG = re.compile(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"')


def words(s):
    return set(re.findall(r'[a-zа-яё0-9]+', html.unescape(s).lower()))


def score(name, title, net):
    a, b = words(name), words(title)
    if not a or not b:
        return 0
    s = len(a & b) / len(a)
    if net and re.search(rf'\b{int(net)}\s*(мл|ml|г|гр)\b', title.lower()):
        s += 0.15   # совпал объём
    return round(min(s, 1.0), 2)


class Command(BaseCommand):
    def add_arguments(self, p):
        p.add_argument('out_csv')
        p.add_argument('--site', required=True, help='например https://cosmetika-premium.by')
        p.add_argument('--brand', required=True, help='часть названия производителя в БД')
        p.add_argument('--limit', type=int, default=0)

    def handle(self, *a, **o):
        site = o['site'].rstrip('/')
        qs = (Product.objects.filter(media__isnull=True, manufacturer__name__icontains=o['brand'])
              .select_related('manufacturer').order_by('id'))
        if o['limit']:
            qs = qs[:o['limit']]
        with open(o['out_csv'], 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'name', 'score', 'found_title', 'image_url', 'product_url'])
            for p in qs:
                row = [p.id, p.name, 0, '', '', '']
                try:
                    r = requests.get(f'{site}/search?q={quote(p.name[:80])}', headers=H, timeout=20)
                    cands = {}
                    for url, inner in LINK.findall(r.text):
                        t = html.unescape(re.sub(r'<[^>]+>', ' ', inner)).strip()
                        if len(t) > 5:
                            cands[url if url.startswith('http') else site + url] = t
                    if cands:
                        url, title = max(cands.items(), key=lambda kv: score(p.name, kv[1], p.net_amount))
                        page = requests.get(url, headers=H, timeout=20).text
                        m = OG.search(page)
                        row = [p.id, p.name, score(p.name, title, p.net_amount), title,
                               html.unescape(m.group(1)) if m else '', url]
                except Exception as e:
                    row[3] = f'ошибка: {e}'
                w.writerow(row)
                time.sleep(1)