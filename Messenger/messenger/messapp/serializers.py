from rest_framework import serializers
from .models import Profile, Chatroom


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatroom
        fields = ('id', 'name')


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name', 'avatar', 'mini_avatar', 'chatroom')