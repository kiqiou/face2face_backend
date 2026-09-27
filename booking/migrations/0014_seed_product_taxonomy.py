from django.db import migrations


SKIN_TYPES = [
    "Возрастная",
    "Возрастная, с морщинами",
    "Для всех типов",
    "Для всех типов с высыпаниями",
    "Для всех типов, в т.ч. для чувствительной",
    "Для всех типов, кроме чувствительной",
    "Жирная",
    "Жирная, с акне",
    "Комбинированная",
    "Нормальная",
    "Сухая",
    "Чувствительная",
    "Акне",
    "Анти-эйдж",
    "Возрастные изменения, снижение тонуса, морщины, нарушен барьер",
    "Обезвоженная",
    "Пигментация",
    "Покраснения",
    "Постакне",
    "Розацеа",
]

PRODUCT_PURPOSES = [
    "Демакияж",
    "Очищение",
    "Глубокое очищение",
    "Тонизация",
    "Сыворотки",
    "Уход для кожи лица",
    "Уход для кожи вокруг глаз",
    "Уход для кожи шеи и декольте",
    "Маски",
    "SPF",
    "Ретинол",
    "Бальзамы для губ",
    "Декоративная косметика",
    "Уход для тела",
    "Уход для рук",
    "Уход для ног",
    "Уход для волос",
    "Для бровей",
    "Для губ",
    "Для зоны декольте",
    "Для ресниц",
    "Для рук и ног",
]

COLLECTIONS = [
    "Готовые наборы",
    "Ретинол",
    "Витамин С",
    "SPF",
    "Новинки",
    "Бестселлеры",
    "Мини-версии",
    "Гель",
    "Крем",
    "Маска",
    "Масло",
    "Молочко",
    "Набор",
    "Пенка",
    "Сыворотка",
    "Тоник",
    "SPF Фильтры",
    "Антиоксиданты",
    "Ботулоподобные пептиды",
    "Кислоты",
    "Ниацинамид",
    "Отбеливающее",
    "Пептиды",
    "Пробиотики",
]


def seed_taxonomy(apps, schema_editor):
    SkinType = apps.get_model('booking', 'SkinType')
    ProductPurpose = apps.get_model('booking', 'ProductPurpose')
    Collection = apps.get_model('booking', 'Collection')

    for name in SKIN_TYPES:
        SkinType.objects.get_or_create(name=name)

    for name in PRODUCT_PURPOSES:
        ProductPurpose.objects.get_or_create(name=name)

    for name in COLLECTIONS:
        Collection.objects.get_or_create(name=name)


def reverse_seed(apps, schema_editor):
    SkinType = apps.get_model('booking', 'SkinType')
    ProductPurpose = apps.get_model('booking', 'ProductPurpose')
    Collection = apps.get_model('booking', 'Collection')

    SkinType.objects.filter(name__in=SKIN_TYPES).delete()
    ProductPurpose.objects.filter(name__in=PRODUCT_PURPOSES).delete()
    Collection.objects.filter(name__in=COLLECTIONS).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0013_collection_exchangerate_productpurpose_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_taxonomy, reverse_seed),
    ]
