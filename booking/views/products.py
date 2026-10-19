from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from booking.models import Product, Manufacturer, SkinType, ProductPurpose, Collection
from booking.serializers import (
    ProductAdminSerializer, ProductSerializer, ProductCreateSerializer,
    ManufacturerSerializer, SkinTypeSerializer,
    ProductPurposeSerializer, CollectionSerializer,
)
from django.db.models import Q, F
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


def _int_list(request, name):
    """?purpose=1&purpose=2 -> [1, 2]"""
    return [int(v) for v in request.query_params.getlist(name) if v.isdigit()]


@api_view(['GET'])
@permission_classes([AllowAny])
def get_products(request):
    is_staff = request.user.is_authenticated and request.user.is_staff

    products = Product.objects.select_related('manufacturer').prefetch_related(
        'skin_types', 'purposes', 'collections', 'media'
    )

    if ids := _int_list(request, 'manufacturer'):
        products = products.filter(manufacturer_id__in=ids)
    if ids := _int_list(request, 'skin_type'):
        products = products.filter(skin_types__id__in=ids)
    if ids := _int_list(request, 'purpose'):
        products = products.filter(purposes__id__in=ids)
    if ids := _int_list(request, 'collection'):
        products = products.filter(collections__id__in=ids)

    in_stock = request.query_params.get('in_stock')
    if in_stock is not None:
        products = products.filter(in_stock=in_stock.lower() == 'true')

    # --- поиск ---
    search = request.query_params.get('search', '').strip()
    if search:
        for term in search.split():  # каждое слово должно встретиться (AND)
            q = (
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(manufacturer__name__icontains=term)
            )
            if is_staff:  # только для админки
                q |= Q(batch_number__icontains=term)
                q |= Q(conformity_document_number__icontains=term)
            products = products.filter(q)

    products = products.distinct()

    on_sale = request.query_params.get('on_sale')
    if on_sale is not None and on_sale.lower() == 'true':
        products = products.filter(sale_price__isnull=False, sale_price__lt=F('price_amount'))

    # --- сортировка (обязательно стабильная, иначе страницы "плывут") ---
    ordering = request.query_params.get('ordering')
    if ordering in ('price_amount', '-price_amount'):
        products = products.order_by(ordering, '-id')
    else:
        products = products.order_by('-created_at', '-id')

    serializer_class = ProductAdminSerializer if is_staff else ProductSerializer

    paginator = ProductPagination()
    page = paginator.paginate_queryset(products, request)
    serializer = serializer_class(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product(request, product_id):
    product = get_object_or_404(
        Product.objects.select_related('manufacturer').prefetch_related(
            'skin_types', 'purposes', 'collections'
        ),
        id=product_id
    )
    is_staff = request.user.is_authenticated and request.user.is_staff
    serializer_class = ProductAdminSerializer if is_staff else ProductSerializer
    print(f"Using serializer: {serializer_class.__name__}")  # Debugging line
    serializer = serializer_class(product)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def add_product(request):
    serializer = ProductCreateSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductAdminSerializer(product).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductCreateSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductAdminSerializer(product).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return Response({'detail': 'Продукт удалён'}, status=status.HTTP_204_NO_CONTENT)


# --- справочники (manufacturer.py у вас уже частично есть — вот полный набор) ---

@api_view(['GET'])
@permission_classes([AllowAny])
def get_manufacturers(request):
    return Response(ManufacturerSerializer(Manufacturer.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_manufacturer(request):
    serializer = ManufacturerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_manufacturer(request, manufacturer_id):
    try:
        manufacturer = Manufacturer.objects.get(id=manufacturer_id)
    except Manufacturer.DoesNotExist:
        return Response({'error': 'Производитель не найден или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ManufacturerSerializer(manufacturer, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_manufacturer(request, manufacturer_id):
    try:
        manufacturer = Manufacturer.objects.get(id=manufacturer_id)
    except Manufacturer.DoesNotExist:
        return Response({'error': 'Производитель не найден или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    manufacturer.delete()
    return Response({'detail': 'Производитель удален'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_skin_types(request):
    return Response(SkinTypeSerializer(SkinType.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_skin_type(request):
    serializer = SkinTypeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_skin_type(request, skin_type_id):
    try:
        skin_type = SkinType.objects.get(id=skin_type_id)
    except SkinType.DoesNotExist:
        return Response({'error': 'Тип кожи не найден или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SkinTypeSerializer(skin_type, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_skin_type(request, skin_type_id):
    try:
        skin_type = SkinType.objects.get(id=skin_type_id)
    except SkinType.DoesNotExist:
        return Response({'error': 'Тип кожи не найден или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    skin_type.delete()
    return Response({'detail': 'Тип кожи удален'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_purposes(request):
    return Response(ProductPurposeSerializer(ProductPurpose.objects.all(), many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_purpose(request):
    serializer = ProductPurposeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_purpose(request, purpose_id):
    try:
        purpose = ProductPurpose.objects.get(id=purpose_id)
    except ProductPurpose.DoesNotExist:
        return Response({'error': 'Цель не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductPurposeSerializer(purpose, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_purpose(request, purpose_id):
    try:
        purpose = ProductPurpose.objects.get(id=purpose_id)
    except ProductPurpose.DoesNotExist:
        return Response({'error': 'Цель не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    purpose.delete()
    return Response({'detail': 'Цель удалена'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_collections(request):
    collections = Collection.objects.filter(is_active=True)
    return Response(CollectionSerializer(collections, many=True).data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_collection(request):
    serializer = CollectionSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_collection(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response({'error': 'Коллекция не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CollectionSerializer(collection, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_collection(request, collection_id):
    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        return Response({'error': 'Коллекция не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    collection.delete()
    return Response({'detail': 'Коллекция удалена'}, status=status.HTTP_204_NO_CONTENT)