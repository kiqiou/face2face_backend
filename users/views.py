import random
import uuid
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from booking.models import Cosmetologist
from face2face_back import settings
from users.models import PhoneVerificationCode, Role, User
from users.serializers.user import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import random
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.cache import cache

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
def login_or_register(request):
    phone = request.data.get('phone')

    if not phone:
        return Response({'error': 'Номер телефона обязателен'}, status=status.HTTP_400_BAD_REQUEST)

    phone = phone.strip()

    user = User.objects.filter(phone=phone).first()
    if user:
        created = False
    else:
        role = Role.objects.get_or_create(name='client')[0]
        user = User.objects.create(username=phone, phone=phone, role=role, is_active=False)
        created = True

    return Response({
        'detail': 'Код отправлен на номер телефона',
        'user_exists': not created
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def confirm_phone_code(request):
    phone = request.data.get('phone')
    code = request.data.get('code')

    if not phone or not code:
        return Response({'error': 'Телефон и код обязательны'}, status=400)

    phone = phone.strip()

    cached_code = cache.get(f"tg_code:{phone}")

    if not cached_code:
         return Response({'error': 'Код истёк'}, status=400)

    if cached_code != code:
        return Response({'error': 'Неверный код'}, status=400)

    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={
            "username": phone,
            "is_active": True,
        }
    )
    
    if user.role_id == 2 or str(user.role) == "cosmetologist": 
        try:
            cosmetologist_profile = Cosmetologist.objects.get(user_id=user.id)
            cosmetologist_data = {'id': cosmetologist_profile.id}
            print(f"Cosmetologist профиль найден: {cosmetologist_profile.id}")
        except Cosmetologist.DoesNotExist:
            print(f"Cosmetologist профиль НЕ НАЙДЕН для user_id={user.id}")
            cosmetologist_data = None
    else:
        cosmetologist_data = None
    user.is_active = True

    telegram_id = cache.get(f"tg_chat:{phone}")

    if telegram_id:
        user.telegram_id = telegram_id
        user.save(update_fields=["telegram_id"])
        cache.set(f"user:{user.id}:chat", telegram_id, 86400 * 30) 

    # if telegram_id:
    #     existing_user = User.objects.filter(telegram_id=telegram_id).exclude(id=user.id).first()
    #     if existing_user:
    #         existing_user.telegram_id = None
    #         existing_user.save(update_fields=["telegram_id"])

    #     user.telegram_id = telegram_id
    #     user.save(update_fields=["telegram_id"])

    #     cache.set(f"user:{user.id}:chat", telegram_id, 86400 * 30)

    if not user.username or user.username.startswith('temp_'):
        user.username = phone
    user.save()

    tokens = get_tokens_for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'access': tokens['access'],
        'cosmetologist_profile': cosmetologist_data,
        'refresh': tokens['refresh'],
        'detail': 'Телефон подтвержден'
    }, status=200)

@api_view(['POST'])
def resend_code(request):
    phone = request.data.get('phone')

    token = uuid.uuid4().hex
    cache.set(f"auth_pending:{token}", phone, 300)

    return Response({
        "telegram_link": f"https://t.me/{settings.TELEGRAM_BOT_NAME}?start={token}"
    })

@api_view(['POST'])
def generate_auth_token(request):
    phone = request.data.get('phone')
    token = uuid.uuid4().hex

    print(f"token: {token}")
    
    cache.set(f"auth_pending:{token}", phone, 300)
    deep_link = f"https://t.me/{settings.TELEGRAM_BOT_NAME}?start={token}"
    
    return Response({
        'auth_token': token,
        'telegram_link': deep_link,
        'message': 'Перейдите по ссылке для подтверждения номера'
    })
