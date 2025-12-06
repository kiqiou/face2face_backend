import random
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from users.models import PhoneVerificationCode, Role, User
from users.serializers.user import UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import random
import string

def generate_random_username(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    while True:
        username = ''.join(random.choice(letters_and_digits) for i in range(length))
        if not User.objects.filter(username=username).exists():
            return username

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

    user, created = User.objects.get_or_create(
        phone=phone,
        defaults={
            'username': phone,
            'role': Role.objects.get_or_create(name='client')[0],
            'is_active': False
        }
    )

    # Генерация кода для подтверждения
    code = str(random.randint(100000, 999999))
    PhoneVerificationCode.objects.update_or_create(
        phone=phone,
        defaults={'code': code, 'is_verified': False, 'created_at': timezone.now()}
    )

    print(f"SMS код для {phone}: {code}")  # TODO: заменить на реальную отправку SMS

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

    try:
        verification = PhoneVerificationCode.objects.get(phone=phone)
    except PhoneVerificationCode.DoesNotExist:
        return Response({'error': 'Код не найден'}, status=400)

    if verification.is_expired():
        return Response({'error': 'Код просрочен'}, status=400)

    if verification.code != code:
        return Response({'error': 'Неверный код'}, status=400)

    verification.is_verified = True
    verification.save()

    user = User.objects.get(phone=phone)
    user.is_active = True
    if not user.username or user.username.startswith('temp_'):
        user.username = generate_random_username()
    user.save()

    tokens = get_tokens_for_user(user)

    return Response({
        'user': UserSerializer(user).data,
        'access': tokens['access'],
        'refresh': tokens['refresh'],
        'detail': 'Телефон подтвержден'
    }, status=200)

@api_view(['POST'])
def resend_code(request):
    phone = request.data.get('phone')
    if not phone:
        return Response({'error': 'Телефон обязателен'}, status=400)

    if not User.objects.filter(phone=phone).exists():
        return Response({'error': 'Пользователь не найден'}, status=404)

    code = str(random.randint(100000, 999999))
    PhoneVerificationCode.objects.update_or_create(
        phone=phone,
        defaults={'code': code, 'is_verified': False, 'created_at': timezone.now()}
    )
    print(f"Повторный SMS-код для {phone}: {code}")
    return Response({'detail': 'Код отправлен повторно'}, status=200)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['PATCH'])
@parser_classes([MultiPartParser, FormParser])
def update_avatar(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    avatar = request.data.get('avatar')
    if not avatar:
        return Response({'error': 'Аватар не передан'}, status=400)

    user.avatar = avatar
    user.save()

    serializer = UserSerializer(user, context={'request': request})

    return Response({
        'detail': 'Аватар обновлен',
        'user': serializer.data
    }, status=200)
