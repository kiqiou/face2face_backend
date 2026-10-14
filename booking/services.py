# booking/services.py
from decimal import Decimal
from django.db.models import Sum, F
from django.utils import timezone

from booking.models import OrderItem, PromoCode, PromoCodeUsage, LoyaltyTier


def get_user_total_spent(user) -> Decimal:
    total = OrderItem.objects.filter(
        order__user=user, order__status='done'
    ).aggregate(total=Sum(F('price_at_order') * F('quantity')))['total']
    return total or Decimal('0')


def get_loyalty_discount_percent(user) -> int:
    if user.manual_discount_percent is not None:
        return user.manual_discount_percent

    total = get_user_total_spent(user)
    tier = LoyaltyTier.objects.filter(min_total_spent__lte=total).order_by('-min_total_spent').first()
    return tier.discount_percent if tier else 0


def validate_promo_code(code: str, user):
    try:
        promo = PromoCode.objects.get(code=code)
    except PromoCode.DoesNotExist:
        return None

    if not promo.is_valid():
        return None
    if PromoCodeUsage.objects.filter(promo_code=promo, user=user).exists():
        return None
    if promo.is_first_order_only and OrderItem.objects.filter(order__user=user, order__status='done').exists():
        return None

    return promo


def resolve_discount(user, promo_code_str):
    loyalty_percent = get_loyalty_discount_percent(user)
    promo = validate_promo_code(promo_code_str, user) if promo_code_str else None
    promo_percent = promo.discount_percent if promo else 0

    if promo_percent >= loyalty_percent:
        return promo_percent, promo
    return loyalty_percent, None