from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from booking.models import Cosmetologist, Manufacturer, Procedure
from booking.serializers import ManufacturerSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_manufacturers(request):
    manufacturers = Manufacturer.objects.all()
    serializer = ManufacturerSerializer(manufacturers, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_manufacturer(request):
    serializer = ManufacturerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
