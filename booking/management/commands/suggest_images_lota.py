import csv, re, html
from urllib.parse import urljoin

import requests
from django.core.management.base import BaseCommand

from booking.models import Product

H = {'User-Agent': 'Mozilla/5.0'}
SITE = 'https://lota.by'

# данные каталога вшиты в HTML как экранированный JSON (\"name\":\"...\")
ITEM = re.compile(
    r'\\"name\\":\\"([^"\\]+)\\",\\"slug\\":\\"[^"\\]*\\".*?'
    r'\\"volume\\":\\"([^"\\]*)\\".*?\\"imageUrl\\":\\"([^"\\]*)\\"', re.S)

# латинские буквы-двойники внутри русских слов («Cолнцезащитный»)
LOOK = str.maketrans('caeopxy', 'саеорху')


def words(s):
    out = set()
    for tok in re.findall(r'[a-zа-яё0-9]+', html.unescape(s).lower()):
        if re.search('[а-яё]', tok):
            tok = tok.translate(LOOK)
        out.add(tok)
    return out


def score(name, title, net):
    a, b = words(name), words(title)
    if not a or not b:
        return 0
    common = len(a & b)
    s = max(common / len(a), 0.9 * common / len(b))
    if net and re.search(rf'\b{int(net)}\s*(мл|ml|г|гр)\b', title.lower()):
        s += 0.15
    return round(min(s, 1.0), 2)


class Command(BaseCommand):
    def add_arguments(self, p):
        p.add_argument('out_csv')
        p.add_argument('--brand', default='lota')

    def handle(self, *a, **o):
        page = requests.get(f'{SITE}/catalog', headers=H, timeout=20).text
        items = {}
        for name, volume, img in ITEM.findall(page):
            items[name] = (volume, img)
        self.stdout.write(f'на сайте найдено препаратов: {len(items)}')

        qs = (Product.objects.filter(media__isnull=True, manufacturer__name__icontains=o['brand'])
              .order_by('id'))
        with open(o['out_csv'], 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'name', 'score', 'found_title', 'image_url', 'product_url', 'size_kb'])
            for p in qs:
                best, best_s = None, 0
                for title, (volume, img) in items.items():
                    s = score(p.name, f'{title} {volume}', p.net_amount)
                    if s > best_s:
                        best, best_s = (title, img), s
                row = [p.id, p.name, 0, '', '', '', '']
                if best and best_s >= 0.3:
                    url = urljoin(SITE, best[1])
                    try:
                        size = round(len(requests.get(url, headers=H, timeout=20).content) / 1024)
                    except Exception:
                        size = ''
                    row = [p.id, p.name, best_s, best[0], url, f'{SITE}/catalog', size]
                w.writerow(row)
                self.stdout.write(f'{p.id}  score={row[2]}  {row[3][:50]}')