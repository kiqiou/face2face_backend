from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from booking.views.booking import calculate_free_intervals
from users.models import User
from booking.models import Category, Cosmetologist, Procedure, Booking, WorkDay
from booking.serializers import (
    CategorySerializer, CosmetologistSerializer, ProcedureSerializer, BookingSerializer, WorkDaySerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_cosmetologists(request):
    cosmetologists = Cosmetologist.objects.all()
    serializer = CosmetologistSerializer(cosmetologists, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cosmetologist_by_id(request, cosmetologist_id):
    cosmetologist = Cosmetologist.objects.get(
        id=cosmetologist_id,
    )
    serializer = CosmetologistSerializer(cosmetologist, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_cosmetologist_by_user_id(request, user_id):
    cosmetologist = Cosmetologist.objects.get(
        user__id=user_id,
    )
    serializer = CosmetologistSerializer(cosmetologist, context={'request': request})
    return Response(serializer.data)

from django.http import JsonResponse

@api_view(['GET'])
@permission_classes([AllowAny])
def list_procedures(request):
    try:
        procedures = Procedure.objects.all()
        serializer = ProcedureSerializer(procedures, many=True)
        return JsonResponse(serializer.data, safe=False)
    except Exception as e:
        # Логируем ошибку
        import traceback
        traceback.print_exc()
        return JsonResponse(
            {'error': str(e), 'traceback': traceback.format_exc()}, 
            status=500
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def list_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_all_work_days(request):
    work_days = WorkDay.objects.filter(is_working=True).prefetch_related('cosmetologist')
    serializer = WorkDaySerializer(work_days, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_work_days_by_cosmetologist(request, cosmetologist_id):
    work_days = WorkDay.objects.filter(
        cosmetologist_id=cosmetologist_id,
        is_working=True
    )

    serializer = WorkDaySerializer(work_days, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_free_intervals(request, work_day_id):
    try:
        work_day = WorkDay.objects.get(id=work_day_id, is_working=True)
    except WorkDay.DoesNotExist:
        return Response({'error': 'Рабочий день не найден'}, status=404)

    free = calculate_free_intervals(work_day)

    free_list = [
        {"start": start.strftime("%H:%M"), "end": end.strftime("%H:%M")}
        for start, end in free
    ]

    return Response(free_list)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_procedures_by_cosmetologist(request, cosmetologist_id):
    procedures = Procedure.objects.filter(cosmetologist_id=cosmetologist_id,)
    serializer = ProcedureSerializer(procedures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_bookings(request):
    bookings = Booking.objects.filter(user=request.user, status=True)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cosmetologist_bookings(request):
    try:
        cosmetologist = Cosmetologist.objects.get(user=request.user)
    except Cosmetologist.DoesNotExist:
        return Response({'detail': 'Вы не косметолог'}, status=400)

    bookings = Booking.objects.filter(cosmetologist=cosmetologist, status=True)
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_bookings(request):
    bookings = Booking.objects.filter(status=True)
    serializer = BookingSerializer(bookings, many=True, context={'request': request})
    return Response(serializer.data)
