from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from booking.models import Order
from django.db.models import Sum, F, Count, DecimalField, ExpressionWrapper
from django.db.models.functions import TruncDate
from booking.models import OrderItem
from booking.serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def create_order(request):
    serializer = OrderCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_orders(request):
    orders = Order.objects.prefetch_related('items__product').all()

    status_filter = request.query_params.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    orders = orders.order_by('-created_at')
    return Response(OrderSerializer(orders, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order_by_id(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'), id=order_id
    )
    return Response(OrderSerializer(order).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related('items__product')
        .order_by('-created_at')
    )
    return Response(OrderSerializer(orders, many=True).data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(OrderSerializer(order).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    return Response({'detail': 'Заказ удалён'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_analytics(request):
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    exclude_cancelled = request.query_params.get('exclude_cancelled', 'true').lower() == 'true'

    items = OrderItem.objects.select_related('order', 'product')
    orders_qs = Order.objects.all()

    if exclude_cancelled:
        items = items.exclude(order__status='cancelled')
        orders_qs = orders_qs.exclude(status='cancelled')
    if date_from:
        items = items.filter(order__created_at__date__gte=date_from)
        orders_qs = orders_qs.filter(created_at__date__gte=date_from)
    if date_to:
        items = items.filter(order__created_at__date__lte=date_to)
        orders_qs = orders_qs.filter(created_at__date__lte=date_to)

    items = items.annotate(
        calculated_revenue=ExpressionWrapper(
            F('price_at_order') * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        ),
        calculated_cost=ExpressionWrapper(
            F('cost_price_at_order') * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    totals = items.aggregate(
        revenue=Sum('calculated_revenue'),
        cost=Sum('calculated_cost'),
        items_sold=Sum('quantity'),
    )
    gross_revenue = totals['revenue'] or 0
    cost = totals['cost'] or 0

    # скидка — отдельным запросом по Order, иначе задвоится при join с OrderItem
    total_discount = orders_qs.aggregate(discount=Sum('discount_amount'))['discount'] or 0

    revenue = gross_revenue - total_discount  # ← чистая выручка с учётом скидок
    profit = revenue - cost
    margin = round((profit / revenue) * 100, 2) if revenue else 0

    orders_count = orders_qs.count()
    avg_order_value = round(revenue / orders_count, 2) if orders_count else 0

    # ---- daily: добавляем скидку по дням отдельным запросом ----
    daily = (
        items.annotate(day=TruncDate('order__created_at'))
        .values('day')
        .annotate(revenue=Sum('calculated_revenue'), cost=Sum('calculated_cost'))
        .order_by('day')
    )

    daily_discounts = (
        orders_qs.annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(discount=Sum('discount_amount'))
    )
    discount_by_day = {d['day']: float(d['discount'] or 0) for d in daily_discounts}

    daily_data = [
        {
            'date': d['day'].isoformat(),
            'revenue': float(d['revenue'] or 0) - discount_by_day.get(d['day'], 0),
            'cost': float(d['cost'] or 0),
            'profit': float(d['revenue'] or 0) - discount_by_day.get(d['day'], 0) - float(d['cost'] or 0),
        }
        for d in daily
    ]

    top_products = (
        items.values('product__id', 'product__name')
        .annotate(quantity=Sum('quantity'), revenue=Sum('calculated_revenue'), cost=Sum('calculated_cost'))
        .order_by('-revenue')[:10]
    )
    top_products_data = [
        {
            'id': p['product__id'],
            'name': p['product__name'],
            'quantity': p['quantity'],
            'revenue': float(p['revenue'] or 0),  # скидка на заказ, не на конкретный товар — тут оставляем gross
            'cost': float(p['cost'] or 0),
            'profit': float((p['revenue'] or 0) - (p['cost'] or 0)),
        }
        for p in top_products
    ]

    status_breakdown = list(
        Order.objects.values('status').annotate(count=Count('id')).order_by('status')
    )

    return Response({
        'summary': {
            'gross_revenue': float(gross_revenue),
            'total_discount': float(total_discount),
            'revenue': float(revenue),
            'cost': float(cost),
            'profit': float(profit),
            'margin_percent': float(margin),
            'orders_count': orders_count,
            'items_sold': totals['items_sold'] or 0,
            'avg_order_value': float(avg_order_value),
        },
        'daily': daily_data,
        'top_products': top_products_data,
        'status_breakdown': status_breakdown,
    })