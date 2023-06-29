from django.contrib import admin
from .models import Profile, Chatroom, Message

admin.site.register(Profile)
admin.site.register(Chatroom)
admin.site.register(Message)
