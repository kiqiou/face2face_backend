# booking/views/clients.py
from django.db import models
from django.db.models import Sum, F, Count, DecimalField, ExpressionWrapper
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from booking.models import OrderItem
from booking.views.promotions import get_loyalty_discount_percent
from users.models import User


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_clients(request):
    search = request.query_params.get('search', '').strip()

    items = OrderItem.objects.filter(order__status='done').annotate(
        revenue=ExpressionWrapper(
            F('price_at_order') * F('quantity'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    totals_by_user = (
        items.values('order__user_id')
        .annotate(total_spent=Sum('revenue'), orders_count=Count('order_id', distinct=True))
    )
    totals_map = {row['order__user_id']: row for row in totals_by_user}

    users_qs = User.objects.filter(is_staff=True)
    if search:
        users_qs = users_qs.filter(
            models.Q(username__icontains=search) | models.Q(phone__icontains=search)
        )

    clients = []
    for user in users_qs:
        row = totals_map.get(user.id, {'total_spent': 0, 'orders_count': 0})
        clients.append({
            'id': user.id,
            'username': user.username,
            'phone': user.phone,
            'total_spent': float(row['total_spent'] or 0),
            'orders_count': row['orders_count'],
            'manual_discount_percent': user.manual_discount_percent,
            'current_discount_percent': get_loyalty_discount_percent(user),
        })

    clients.sort(key=lambda c: c['total_spent'], reverse=True)
    return Response(clients)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def set_client_discount(request, user_id):
    from django.shortcuts import get_object_or_404
    user = get_object_or_404(User, id=user_id)

    value = request.data.get('manual_discount_percent')

    if value is not None:
        value = int(value)
        if not (0 <= value <= 100):
            return Response({'error': 'Скидка должна быть от 0 до 100'}, status=400)

    user.manual_discount_percent = value  # None — сброс на автоматический расчёт
    user.save(update_fields=['manual_discount_percent'])

    return Response({
        'id': user.id,
        'manual_discount_percent': user.manual_discount_percent,
        'current_discount_percent': get_loyalty_discount_percent(user),
    })