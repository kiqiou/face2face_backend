# products/management/commands/auto_tag_products.py
import re
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from booking.models import Product, Collection, ProductPurpose, SkinType  # поправь путь


def R(p):
    return re.compile(p, re.I)

# scope: name = только название, text = название+описание, all = + состав
COLLECTIONS = [
    ('Готовые наборы', R(r'набор|\bset\b'), 'name'),
    ('Набор',          R(r'набор|\bset\b'), 'name'),
    ('Ретинол',        R(r'ретинол|retinol'), 'all'),
    ('Витамин С',      R(r'витамин\s*с\b|vitamin c|ascorb|\bvit\.?-?c'), 'all'),
    ('SPF',            R(r'spf|спф|солнцезащ|фотозащ|фотоблок'), 'name'),
    ('SPF Фильтры',    R(r'spf|спф|солнцезащ|фотозащ|фотоблок'), 'name'),
    ('Новинки',        R(r'\bnew\b'), 'name'),
    ('Мини-версии',    R(r'\bmini\b|мини'), 'name'),
    ('Гель',           R(r'гель|\bgel\b'), 'name'),
    ('Крем',           R(r'крем|cream'), 'name'),
    ('Маска',          R(r'маск|mask'), 'name'),
    ('Масло',          R(r'масл|\boil\b'), 'name'),
    ('Молочко',        R(r'молочк|milk'), 'name'),
    ('Пенка',          R(r'пенк|foam|мусс|mousse'), 'name'),
    ('Сыворотка',      R(r'сыворотк|serum'), 'name'),
    ('Тоник',          R(r'тоник|тонер|toner|tonic'), 'name'),
    ('Антиоксиданты',  R(r'ascorb|ferul|resveratrol|green tea|superoxide|spin trap|astaxanthin|coenzyme|антиоксидант'), 'all'),
    ('Ботулоподобные пептиды', R(r'hexapeptide-8|argireline|boto|bo2look|миорелакс|ботул|conopeptide'), 'all'),
    ('Кислоты',        R(r'glycolic|lactic acid|salicylic|mandelic|azelaic|lactobionic|shikimic|tranexamic|kojic|malic|кислот'), 'all'),
    ('Ниацинамид',     R(r'niacinamide|ниацинамид'), 'all'),
    ('Отбеливающее',   R(r'осветл|отбелив|депигмент|tranexamic|kojic|arbutin'), 'all'),
    ('Пептиды',        R(r'peptide|пептид'), 'all'),
    ('Пробиотики',     R(r'probiotic|prebiotic|пребиот|пробиот|microbiom|микробиом'), 'all'),
    ('Гиалуроновая кислота', R(r'hyaluron|гиалурон'), 'all'),
    ('Экзосомы',       R(r'\bexo|экзосом'), 'all'),
    ('Фотостарение',   R(r'фотостарен|photoaging|ferul'), 'all'),
    ('Фитоэстрогены',  R(r'phytogen|phytoestrogen|фитоэстроген|red clover|cimicifuga'), 'all'),
]

PURPOSES = [
    ('Демакияж',  R(r'демакияж|мицеллярн|гидрофильн|макияж|cleansing oil|biphasic|двухфазн'), 'text'),
    ('Очищение',  R(r'очища|очищени|умыван|пенк|cleans|мыло|foam'), 'name'),
    ('Глубокое очищение', R(r'пилинг|peel|скраб|scrub|глин|clay|детокс|гоммаж|пэды|энзим'), 'name'),
    ('Тонизация', R(r'тоник|тонер|toner|tonic|мист|спрей|лосьон'), 'name'),
    ('Сыворотки', R(r'сыворотк|serum|эликсир|elixir|бустер|booster|концентрат|капли|drops'), 'name'),
    ('Уход для кожи вокруг глаз', R(r'\bвек|глаз|\beye'), 'name'),
    ('Уход для кожи шеи и декольте', R(r'шеи|декольте|neck|decollete'), 'name'),
    ('Для зоны декольте', R(r'декольте|decollete'), 'name'),
    ('Маски',     R(r'маск|mask'), 'name'),
    ('SPF',       R(r'spf|спф|солнцезащ|фотозащ|фотоблок|sun guard'), 'name'),
    ('Ретинол',   R(r'ретинол|retinol'), 'name'),
    ('Бальзамы для губ', R(r'бальзам для губ|lip repair|coralip'), 'name'),
    ('Для губ',   R(r'\bгуб|\blip'), 'name'),
    ('Декоративная косметика', R(r'тональн|\b(bb|вв|cc)\b|блеск|пудра (комплексная|защитная)'), 'name'),
    ('Уход для тела', R(r'тела|body|бюст|бедер|живот|загар|душа|aftersun|tan\b'), 'name'),
    ('Уход для рук', R(r'для рук|hand'), 'name'),
    ('Уход для ног', R(r'для ног|foot|стоп'), 'name'),
    ('Для рук и ног', R(r'для рук|hand|для ног|foot|стоп'), 'name'),
    ('Для бровей',  R(r'бров'), 'name'),
    ('Для ресниц',  R(r'ресниц'), 'name'),
    ('Уход для волос', R(r'волос'), 'name'),
    ('Аксессуары и гаджеты', R(r'массаж[её]р|гуаша|gua sha|ролик|скребок'), 'name'),
]
FACE_EXCLUDE = {'Уход для тела', 'Уход для рук', 'Уход для ног', 'Для рук и ног',
                'Бальзамы для губ', 'Для губ', 'Аксессуары и гаджеты',
                'Уход для кожи вокруг глаз', 'Уход для кожи шеи и декольте'}

SKIN = [
    ('Жирная',        R(r'жирн'), 'text'),
    ('Комбинированная', R(r'комбинир'), 'text'),
    ('Сухая',         R(r'\bсух|гиперсух'), 'text'),
    ('Обезвоженная',  R(r'обезвожен'), 'text'),
    ('Чувствительная', R(r'чувствительн|реактивн'), 'text'),
    ('Нормальная',    R(r'нормальн'), 'text'),
    ('Возрастная',    R(r'зрел|возраст|антивозраст|anti-?age|омолаж|морщин|лифтинг'), 'text'),
    ('Анти-эйдж',     R(r'антивозраст|anti-?age|омолаж'), 'text'),
    ('Акне',          R(r'акне|acne|угрев|комедон'), 'text'),
    ('Постакне',      R(r'постакне'), 'text'),
    ('Пигментация',   R(r'пигмент|осветл|тусклой'), 'text'),
    ('Покраснения',   R(r'покраснен|купероз|гиперемия'), 'text'),
    ('Розацеа',       R(r'розацеа'), 'text'),
]
SKIN_DEFAULT = 'Для всех типов'


def texts(p):
    name = p.name or ''
    text = f'{name} {p.description or ""}'
    return {'name': name, 'text': text, 'all': f'{text} {p.ingredients or ""}'}


def match(rules, t):
    return [label for label, rx, scope in rules if rx.search(t[scope])]


class Command(BaseCommand):
    help = 'Раздаёт подборки / назначения / типы кожи по ключевым словам'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='без флага — только отчёт')

    @transaction.atomic
    def handle(self, *a, **o):
        cols = {c.name: c for c in Collection.objects.all()}
        purs = {c.name: c for c in ProductPurpose.objects.all()}
        skins = {c.name: c for c in SkinType.objects.all()}

        qs = Product.objects.select_related('manufacturer')
        self.stdout.write(f"Товаров в работе: {qs.count()}")
        self.stdout.write('Производители в работе: ' +
                          ', '.join(sorted({p.manufacturer.name for p in qs})))

        stats = Counter()
        missing = set()
        for p in qs:
            t = texts(p)
            c_labels = match(COLLECTIONS, t)
            p_labels = match(PURPOSES, t)
            if not set(p_labels) & FACE_EXCLUDE:
                p_labels.append('Уход для кожи лица')
            s_labels = match(SKIN, t) or [SKIN_DEFAULT]

            for labels, pool, rel in ((c_labels, cols, p.collections),
                                      (p_labels, purs, p.purposes),
                                      (s_labels, skins, p.skin_types)):
                objs = []
                for l in labels:
                    if l in pool:
                        objs.append(pool[l]); stats[l] += 1
                    else:
                        missing.add(l)
                if o['apply'] and objs:
                    rel.add(*objs)  # add не создаёт дублей

        for k, v in stats.most_common():
            self.stdout.write(f'  {k}: {v}')
        if missing:
            self.stderr.write('Нет в БД: ' + ', '.join(sorted(missing)))
        self.stdout.write(self.style.SUCCESS('Применено' if o['apply'] else 'Сухой прогон, ничего не записано'))