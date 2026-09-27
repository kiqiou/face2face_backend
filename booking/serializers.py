import mimetypes

from rest_framework import serializers
from users.models import User
from booking.models import Category, Cosmetologist, ExchangeRate, Manufacturer, Procedure, Booking, Product, ProductMedia, SkinType, WorkDay
from users.serializers.user import UserSerializer

class CosmetologistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Cosmetologist
        fields = ['user', 'bio', 'specializations', 'id', 'avatar_url']

    def get_avatar_url(self, obj):
        return obj.avatar_url

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProcedureSerializer(serializers.ModelSerializer):
    cosmetologist = CosmetologistSerializer()
    category = CategorySerializer()

    class Meta:
        model = Procedure
        fields = ['id', 'name', 'price', 'duration', 'buffer_time', 'description', 'cosmetologist', 'category']

class ProcedureCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = [
            'name',
            'price',
            'duration',
            'description',
            'buffer_time',
            'category'
        ]

class WorkDaySerializer(serializers.ModelSerializer):
    cosmetologist = CosmetologistSerializer()

    class Meta:
        model = WorkDay
        fields = [
            'id',
            'date',
            'start_time',
            'end_time',
            'is_working',
            'cosmetologist'
        ]

class WorkDayCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkDay
        fields = [
            'id',
            'date',
            'start_time',
            'end_time',
            'is_working'
        ]

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    cosmetologist = CosmetologistSerializer()
    procedures = ProcedureSerializer(many=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'cosmetologist',
            'date',
            'start_time',
            'end_time',
            'duration',
            'price',
            'status',
            'procedures'
        ]

from rest_framework import serializers
from users.models import User
from users.serializers.user import UserSerializer
from booking.models import (
    Category, Cosmetologist, ExchangeRate, Manufacturer, Procedure, Booking,
    Product, SkinType, WorkDay, ProductPurpose, Collection, Order, OrderItem
)

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'address', 'country']

class SkinTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkinType
        fields = ['id', 'name', 'description']


class ProductPurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurpose
        fields = ['id', 'name']


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'name', 'is_active']


class ProductMediaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductMedia
        fields = ['id', 'url', 'media_type', 'order']

    def get_url(self, obj):
        if not obj.file:
            return None
        return obj.file.url


class ProductSerializer(serializers.ModelSerializer):
    """Для чтения — вложенные объекты + цена в USD."""
    manufacturer = ManufacturerSerializer(read_only=True)
    skin_types = SkinTypeSerializer(many=True, read_only=True)
    purposes = ProductPurposeSerializer(many=True, read_only=True)
    collections = CollectionSerializer(many=True, read_only=True)
    media = ProductMediaSerializer(many=True, read_only=True)
    price_usd = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()  # было полем модели — теперь полный URL

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description',
            'price_amount', 'price_currency', 'price_usd',
            'manufacturer', 'skin_types', 'purposes', 'collections',
            'image', 'media', 'in_stock', 'created_at',
            'net_amount', 'net_amount_unit',
            'ingredients', 'shelf_life_months',
            'storage_conditions', 'precautions', 'usage_instructions',
            'is_for_children', 'color_shade', 'fluoride_content',
            'batch_number',
            'conformity_document_number', 'conformity_document_valid_until',
        ]

    def get_price_usd(self, obj):
        if obj.price_currency == 'USD':
            return obj.price_amount
        rate = ExchangeRate.objects.filter(currency='USD').first()
        if not rate:
            return None
        return round(obj.price_amount / rate.rate_to_byn, 2)

    def get_image(self, obj):
        if not obj.image:
            return None
        return obj.image.url


class ProductCreateSerializer(serializers.ModelSerializer):
    manufacturer = serializers.PrimaryKeyRelatedField(queryset=Manufacturer.objects.all())
    skin_types = serializers.PrimaryKeyRelatedField(
        queryset=SkinType.objects.all(), many=True, required=False
    )
    purposes = serializers.PrimaryKeyRelatedField(
        queryset=ProductPurpose.objects.all(), many=True, required=False
    )
    collections = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(), many=True, required=False
    )
    media = serializers.ListField(
        child=serializers.FileField(), required=False, write_only=True
    )
    media_ids_to_delete = serializers.ListField(
        child=serializers.IntegerField(), required=False, write_only=True
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description',
            'price_amount', 'price_currency',
            'manufacturer', 'skin_types', 'purposes', 'collections',
            'image', 'media', 'media_ids_to_delete', 'in_stock',
            'cost_price', 
            'net_amount', 'net_amount_unit',
            'ingredients', 'shelf_life_months',
            'storage_conditions', 'precautions', 'usage_instructions',
            'is_for_children', 'color_shade', 'fluoride_content',
            'batch_number',
            'conformity_document_number', 'conformity_document_valid_until',
        ]
        
    def create(self, validated_data):
        media_files = validated_data.pop('media', [])
        validated_data.pop('media_ids_to_delete', None)
        product = super().create(validated_data)  # тут же корректно проставит m2m (skin_types и т.д.)
        self._save_media(product, media_files)
        return product

    def update(self, instance, validated_data):
        media_files = validated_data.pop('media', [])
        media_ids_to_delete = validated_data.pop('media_ids_to_delete', [])
        product = super().update(instance, validated_data)

        if media_ids_to_delete:
            product.media.filter(id__in=media_ids_to_delete).delete()

        self._save_media(product, media_files)
        return product

    def _save_media(self, product, media_files):
        start_order = product.media.count()
        for i, f in enumerate(media_files):
            content_type = getattr(f, 'content_type', '') or mimetypes.guess_type(f.name)[0] or ''
            media_type = 'video' if content_type.startswith('video') else 'image'
            ProductMedia.objects.create(
                product=product,
                file=f,
                media_type=media_type,
                order=start_order + i,
            )

class ProductAdminSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ['cost_price']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price_at_order', 'cost_price_at_order']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'payment_method', 'approvement_method',
            'comment', 'status', 'created_at', 'items', 
        ]

class OrderItemCreateSerializer(serializers.Serializer):
    """Один товар в заказе на этапе оформления — просто id + количество."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, default=1)


class OrderCreateSerializer(serializers.ModelSerializer):
    """Оформление заказа — принимает список товаров, сам считает цену на момент заказа."""
    items = OrderItemCreateSerializer(many=True, write_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'payment_method', 'approvement_method', 'comment', 'items']

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Заказ не может быть пустым')
        return items

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(
            user=user if user.is_authenticated else None,
            **validated_data
        )
        for item in items_data:
            product = item['product']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price_at_order=product.price_amount,
                cost_price_at_order=product.cost_price,  # фиксируем себестоимость на момент заказа
            )
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']