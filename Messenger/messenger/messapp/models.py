from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField

class Chatroom(models.Model):
    name = models.CharField(max_length=280, unique=True)

class Profile(models.Model):
    name = models.CharField(max_length=280, unique=True)
    avatar = ThumbnailerImageField(resize_source={'size':(300,300), 'crop':'smart'}, upload_to='djangochatserver', default='djangochatserver/default.jpg')
    mini_avatar = ThumbnailerImageField(resize_source={'size': (30, 30), 'crop': 'smart'}, upload_to='djangochatserver', default='djangochatserver/default_small.jpg')
    chatroom = models.OneToOneField(Chatroom, on_delete=models.SET_NULL, null=True)
    online = models.BooleanField(default=False)

    def user(self):
        users = Profile.objects.filter().order_by('name')
        return list(users)

class Message(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    room = models.ForeignKey(Chatroom, on_delete=models.CASCADE)
    text = models.CharField(max_length=280)