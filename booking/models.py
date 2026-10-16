from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.db import models
from django.utils import timezone
from users.models import User

class SkinType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class ExchangeRate(models.Model):
    currency = models.CharField(max_length=3, unique=True) 
    rate_to_byn = models.DecimalField(max_digits=10, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)

class ProductPurpose(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=100, unique=True) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # обязательны по ст.5 п.9.2 ТР ТС 009/2011 — юр.адрес и страна изготовителя
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    CURRENCY_CHOICES = [
        ('BYN', 'BYN'),
        ('USD', 'USD'),
    ]

    UNIT_CHOICES = [
        ('ml', 'мл'),
        ('l', 'л'),
        ('g', 'г'),
        ('kg', 'кг'),
        ('pcs', 'шт'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    price_amount = models.DecimalField(max_digits=10, decimal_places=2)
    price_currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BYN')

    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='products')
    skin_types = models.ManyToManyField(SkinType, related_name='products', blank=True)
    purposes = models.ManyToManyField(ProductPurpose, related_name='products', blank=True)
    collections = models.ManyToManyField(Collection, related_name='products', blank=True)

    image = CloudinaryField('image', blank=True, null=True)
    in_stock = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # --- Обязательные по ТР ТС 009/2011 ст.5 п.9.2 ---
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_amount_unit = models.CharField(max_length=5, choices=UNIT_CHOICES, blank=True)
    ingredients = models.TextField(blank=True)
    shelf_life_months = models.PositiveIntegerField(null=True, blank=True)
    storage_conditions = models.TextField(blank=True)
    precautions = models.TextField(blank=True)
    usage_instructions = models.TextField(blank=True)
    is_for_children = models.BooleanField(default=False)
    color_shade = models.CharField(max_length=100, blank=True)
    fluoride_content = models.CharField(max_length=50, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
        # --- Подтверждение соответствия ---
    conformity_document_number = models.CharField(max_length=100, blank=True)
    conformity_document_valid_until = models.DateField(null=True, blank=True)
    sale_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Акционная цена — если задана и меньше price_amount, товар считается 'по акции'"
    )

    @property
    def effective_price(self):
        """Цена, которая реально применяется — акционная, если она ниже обычной."""
        if self.sale_price is not None and self.sale_price < self.price_amount:
            return self.sale_price
        return self.price_amount

    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price_amount

    def __str__(self):
        return f"{self.name} ({self.manufacturer})"
    
class ProductMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    # resource_type='auto' — обязательно, иначе Cloudinary попытается закинуть видео как картинку и упадёт
    file = CloudinaryField('media', resource_type='auto', blank=True, null=True)
    media_type = models.CharField(max_length=5, choices=MEDIA_TYPE_CHOICES, default='image')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.product.name} — {self.media_type} #{self.id}"

class PromoCode(models.Model):
    code = models.CharField(max_length=32, unique=True)
    discount_percent = models.PositiveSmallIntegerField(help_text="0–100")
    is_first_order_only = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Пусто = без ограничения")
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def __str__(self):
        return self.code


class PromoCodeUsage(models.Model):
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField('booking.Order', on_delete=models.SET_NULL, null=True, blank=True)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('promo_code', 'user')  # один промокод — один раз на юзера


class LoyaltyTier(models.Model):
    """Пороги персональной скидки по сумме выполненных заказов."""
    min_total_spent = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['-min_total_spent']

    def __str__(self):
        return f"от {self.min_total_spent} BYN — {self.discount_percent}%"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтверждён'),
        ('done', 'Выполнен'),
        ('cancelled', 'Отменён'),
    ]
    APPROVEMENT_CHOICES = [
        ('call', 'Позвонить'),
        ('message', 'Написать'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Наличные'),
        ('card', 'Карта'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # SET_NULL, а не CASCADE — заказ должен пережить удаление аккаунта, для бухгалтерии
    approvement_method = models.CharField(max_length=10, choices=APPROVEMENT_CHOICES)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES)
    comment = models.TextField(blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    # фиксируем цену на момент заказа — если товар подорожает завтра, старый заказ не должен пересчитаться
    # booking/models.py, в Order
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, null=True, blank=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    # PROTECT — чтобы нельзя было случайно удалить товар, на который есть история заказов
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price_at_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)



