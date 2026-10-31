import csv, re, time, html
from urllib.parse import quote, urljoin
import requests
from django.core.management.base import BaseCommand
from booking.models import Product

H = {'User-Agent': 'Mozilla/5.0'}
ENGINES = {
    'insales': '{site}/search?q={q}',
    'woo':     '{site}/?s={q}&post_type=product',
    'bitrix':  '{site}/search/index.php?q={q}',
}
OG = [
    re.compile(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', re.I),
    re.compile(r'data-large_image=["\']([^"\']+)', re.I),
]
UPLOAD = re.compile(r'<img[^>]+src=["\']([^"\']*(?:/upload/|wp-content/uploads)[^"\']+)', re.I)


def words(s):
    return set(re.findall(r'[a-zа-яё0-9]+', html.unescape(s).lower()))


def score(name, title, net):
    a, b = words(name), words(title)
    if not a or not b:
        return 0
    common = len(a & b)
    s = max(common / len(a), 0.9 * common / len(b))   # в обе стороны
    if net and re.search(rf'\b{int(net)}\s*(мл|ml|г|гр)\b', title.lower()):
        s += 0.15
    return round(min(s, 1.0), 2)


def queries(name):
    ws = name.split()
    cyr = ' '.join(w for w in ws if re.search('[а-яё]', w, re.I))
    lat = ' '.join(w for w in ws if not re.search('[а-яё]', w, re.I))
    out = []
    for q in (name, lat, cyr, ' '.join(ws[:3])):
        q = q.strip(' «»"')
        if len(q) > 2 and q not in out:
            out.append(q)
    return out


def pick_image(page, base):
    for rx in OG:
        m = rx.search(page)
        if m:
            return urljoin(base, html.unescape(m.group(1)))
    m = UPLOAD.search(page)
    return urljoin(base, html.unescape(m.group(1))) if m else ''


class Command(BaseCommand):
    def add_arguments(self, p):
        p.add_argument('out_csv')
        p.add_argument('--site', required=True)
        p.add_argument('--brand', required=True, help='часть названия производителя в БД')
        p.add_argument('--engine', choices=list(ENGINES), default='insales')
        p.add_argument('--search', help='свой шаблон адреса поиска: {site}/...{q}')
        p.add_argument('--catalog', help='шаблон адреса списка товаров с {n} для номера страницы')
        p.add_argument('--link', default='/product/', help='часть адреса карточки товара')
        p.add_argument('--limit', type=int, default=0)

    def handle(self, *a, **o):
        site = o['site'].rstrip('/')
        tpl = o['search'] or ENGINES[o['engine']]
        link_rx = re.compile(
            rf'<a[^>]+href="([^"]*?{re.escape(o["link"])}[^"#?]+)[^"]*"[^>]*>(.*?)</a>', re.S)

        def collect(text, into):
            for url, inner in link_rx.findall(text):
                t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', inner))).strip()
                u = urljoin(site + '/', url)
                if len(t) > 5 and not t.startswith('http') and len(t) > len(into.get(u, '')):
                    into[u] = t

        catalog = {}
        if o['catalog']:
            for n in range(1, 31):
                before = len(catalog)
                r = requests.get(o['catalog'].format(n=n), headers=H, timeout=15)
                collect(r.text, catalog)
                self.stdout.write(f'страница {n}: новых {len(catalog) - before}')
                if len(catalog) == before:
                    break
                time.sleep(1)
            self.stdout.write(f'в каталоге сайта: {len(catalog)} товаров')

        qs = (Product.objects.filter(media__isnull=True, manufacturer__name__icontains=o['brand'])
              .select_related('manufacturer').order_by('id'))
        if o['limit']:
            qs = qs[:o['limit']]
        with open(o['out_csv'], 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f)
            w.writerow(['id', 'name', 'score', 'found_title', 'image_url', 'product_url'])
            for p in qs:
                row = [p.id, p.name, 0, '', '', '']
                cands = dict(catalog)
                try:
                    if not catalog:
                        best = 0
                        for q in queries(p.name):
                            r = requests.get(tpl.format(site=site, q=quote(q)), headers=H, timeout=15)
                            collect(r.text, cands)
                            if cands:
                                best = max(score(p.name, t, p.net_amount) for t in cands.values())
                            if best >= 0.7:
                                break
                            time.sleep(0.5)
                    if cands:
                        url, title = max(cands.items(), key=lambda kv: score(p.name, kv[1], p.net_amount))
                        sc = score(p.name, title, p.net_amount)
                        if sc >= 0.3:
                            page = requests.get(url, headers=H, timeout=15).text
                            row = [p.id, p.name, sc, title[:120], pick_image(page, url), url]
                except Exception as e:
                    row[3] = f'ошибка: {e}'
                w.writerow(row)
                f.flush()
                self.stdout.write(f"{p.id}  кандидатов={len(cands)}  score={row[2]}  {row[3][:50]}")
                if not catalog:
                    time.sleep(1)