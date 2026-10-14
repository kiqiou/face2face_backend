# promotions/services.py
from decimal import Decimal
from django.db.models import Sum, F
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from booking.models import OrderItem
from booking.models import LoyaltyTier, PromoCode, PromoCodeUsage
from booking.serializers import PromoCodeSerializer, PromoCodeSerializerRead
from django.shortcuts import get_object_or_404
from booking.services import get_user_total_spent, get_loyalty_discount_percent, validate_promo_code

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_promo_code(request):
    code = request.data.get('code', '').strip()

    if not code:
        return Response({'error': 'Введите промокод'}, status=400)

    promo = validate_promo_code(code, request.user)

    if not promo:
        return Response({'valid': False, 'error': 'Промокод недействителен или уже использован'}, status=400)

    return Response({'valid': True, 'discount_percent': promo.discount_percent, 'code': promo.code})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_discount(request):
    total = get_user_total_spent(request.user)
    current_percent = get_loyalty_discount_percent(request.user)

    next_tier = (
        LoyaltyTier.objects.filter(min_total_spent__gt=total)
        .order_by('min_total_spent')
        .first()
    )

    return Response({
        'total_spent': float(total),
        'current_discount_percent': current_percent,
        'next_tier_threshold': float(next_tier.min_total_spent) if next_tier else None,
        'next_tier_discount_percent': next_tier.discount_percent if next_tier else None,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def promo_codes_list(request):
    if request.method == 'GET':
        promos = PromoCode.objects.all().order_by('-created_at')
        return Response(PromoCodeSerializerRead(promos, many=True).data)

    serializer = PromoCodeSerializerRead(data=request.data)
    if serializer.is_valid():
        promo = serializer.save()
        return Response(PromoCodeSerializerRead(promo).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAdminUser])
def promo_code_detail(request, promo_id):
    promo = get_object_or_404(PromoCode, id=promo_id)

    if request.method == 'DELETE':
        promo.delete()
        return Response(status=204)

    serializer = PromoCodeSerializerRead(promo, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(PromoCodeSerializerRead(promo).data)
    return Response(serializer.errors, status=400)