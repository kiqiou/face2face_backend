# promotions/urls.py
from django.urls import path
from booking.views.promotions import check_promo_code, my_discount, promo_code_detail, promo_codes_list

urlpatterns = [
    path('check-promo/', check_promo_code),
    path('my-discount/', my_discount),
    path('promo-codes/', promo_codes_list),
    path('promo-codes/<int:promo_id>/', promo_code_detail),
]