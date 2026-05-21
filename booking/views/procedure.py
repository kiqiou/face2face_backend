from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking.models import Cosmetologist, Procedure
from booking.serializers import ProcedureSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_procedure(request):
    user = request.user

    serializer = ProcedureSerializer(data=request.data)
    if serializer.is_valid():
        cosmetologist = Cosmetologist.objects.get(user=user.id)
        serializer.save(cosmetologist=cosmetologist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_procedure(request, procedure_id):
    user = request.user
    try:
        procedure = Procedure.objects.get(id=procedure_id, cosmetologist=user.cosmetologist_profile)
    except Procedure.DoesNotExist:
        return Response({'error': 'Процедура не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProcedureSerializer(procedure, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_procedure(request, procedure_id):
    user = request.user
    try:
        procedure = Procedure.objects.get(id=procedure_id, cosmetologist=user.cosmetologist_profile)
    except Procedure.DoesNotExist:
        return Response({'error': 'Процедура не найдена или доступ запрещен'}, status=status.HTTP_404_NOT_FOUND)

    procedure.delete()
    return Response({'detail': 'Процедура удалена'}, status=status.HTTP_204_NO_CONTENT)
