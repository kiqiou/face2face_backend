import uuid
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import Cosmetologist
from face2face_back import settings
from users.models import Role, User
from users.serializers.user import UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@api_view(['POST'])
def generate_auth_token(request):
    # телефон с фронта больше НЕ принимаем — только генерируем токен
    token = uuid.uuid4().hex
    cache.set(f"auth_pending:{token}", True, 300)  # просто маркер "ждём подтверждения"

    return Response({
        'auth_token': token,
        'telegram_link': f"https://t.me/{settings.TELEGRAM_BOT_NAME}?start={token}",
    })


import re
from django.core.exceptions import ValidationError

PHONE_RE = re.compile(r'^\+375\d{9}$')


@api_view(['GET'])
def check_auth_status(request, token):
    result = cache.get(f"auth_result:{token}")

    if not result:
        return Response({'status': 'pending'})

    phone = result['phone']
    telegram_id = result['chat_id']

    if not PHONE_RE.match(phone):
        cache.delete(f"auth_result:{token}")
        return Response(
            {'status': 'error', 'error': 'Вход возможен только с белорусским номером телефона (+375...)'},
            status=400,
        )

    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={'username': phone, 'is_active': True},
    )

    if user.telegram_id != telegram_id:
        # отвязываем этот telegram_id от прежнего владельца, если он был
        User.objects.filter(telegram_id=telegram_id).exclude(id=user.id).update(telegram_id=None)

        user.telegram_id = telegram_id
        user.is_active = True
        user.save(update_fields=['telegram_id', 'is_active'])

    cosmetologist_data = None
    if user.role_id == 2 or str(user.role) == "cosmetologist":
        cosmetologist_profile = Cosmetologist.objects.filter(user_id=user.id).first()
        if cosmetologist_profile:
            cosmetologist_data = {'id': cosmetologist_profile.id}

    tokens = get_tokens_for_user(user)
    cache.delete(f"auth_result:{token}")

    return Response({
        'status': 'confirmed',
        'user': UserSerializer(user).data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'cosmetologist_profile': cosmetologist_data,
    })