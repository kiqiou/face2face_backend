import random
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from users.models import PhoneVerificationCode, Role, User
from users.serializers.user import UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def register_user(request):
    phone = request.data.get('phone')

    if not phone:
        return Response({'error': 'Номер телефона обязателен'}, status=400)

    user, created = User.objects.get_or_create(phone=phone, defaults={
        'username': phone,
        'role': Role.objects.get_or_create(name='client')[0],
        'is_active': False
    })

    code = str(random.randint(100000, 999999))
    PhoneVerificationCode.objects.update_or_create(
        phone=phone,
        defaults={'code': code, 'is_verified': False, 'created_at': timezone.now()}
    )

    # TODO: отправить SMS через API (например, Twilio или smsc.ru)
    print(f"SMS код для {phone}: {code}")

    return Response({'detail': 'Код отправлен на номер телефона'}, status=201)


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

class UpdateAvatarView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        avatar = request.data.get('avatar')

        if not avatar:
            return Response({'error': 'Аватар не передан'}, status=400)

        user.avatar = avatar
        user.save()
        return Response({'detail': 'Аватар обновлен', 'user': UserSerializer(user).data})
