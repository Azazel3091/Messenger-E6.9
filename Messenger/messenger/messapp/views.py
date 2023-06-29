from django.http import JsonResponse
from .models import Profile, Chatroom
from .serializers import RoomSerializer, UserProfileSerializer
from rest_framework.viewsets import ModelViewSet


def api_users(request):
    if request.method == 'GET':
        users = Profile.objects.all()
        serializer = UserProfileSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)


class UsersApi(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = UserProfileSerializer


class RoomsApi(ModelViewSet):
    queryset = Chatroom.objects.all()
    serializer_class = RoomSerializer