from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from booking.models import SkinType
from booking.serializers import SkinTypeSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_skin_types(request):
    skin_types = SkinType.objects.all()
    serializer = SkinTypeSerializer(skin_types, many=True)
    return Response(serializer.data)