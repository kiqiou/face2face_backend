from django.utils import timezone
import uuid
from django.core.cache import cache
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from face2face_back import settings
from users.models import User
from users.serializers.user import UserSerializer


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@api_view(['POST'])
def generate_auth_token(request):
    if not request.data.get('consent'):
        return Response({'error': 'Необходимо согласие на обработку персональных данных'}, status=400)

    token = uuid.uuid4().hex
    cache.set(f"auth_pending:{token}", {
        'consent_at': timezone.now().isoformat(),
        'consent_ip': request.META.get('REMOTE_ADDR'),
    }, 300)

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
    pending_data = cache.get(f"auth_pending:{token}") or {}

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
        defaults={
            'username': phone,
            'is_active': True,
            'personal_data_consent_at': pending_data.get('consent_at'),
            'personal_data_consent_ip': pending_data.get('consent_ip'),
        },
    )

    if user.telegram_id != telegram_id:
        # отвязываем этот telegram_id от прежнего владельца, если он был
        User.objects.filter(telegram_id=telegram_id).exclude(id=user.id).update(telegram_id=None)

        user.telegram_id = telegram_id
        user.is_active = True
        user.save(update_fields=['telegram_id', 'is_active'])

    tokens = get_tokens_for_user(user)
    cache.delete(f"auth_result:{token}")

    return Response({
        'status': 'confirmed',
        'user': UserSerializer(user).data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    })