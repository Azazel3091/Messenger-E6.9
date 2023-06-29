import json
from .models import Profile, Chatroom, Message
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


def userlist():
    objects = Profile.objects.filter().order_by('-name')
    list = {'UserList': 'UserList'}
    for object in objects:
        list[object.id] = object.name
    return list


def roomlist():
    objects = Chatroom.objects.filter()
    list = {'RoomList': 'RoomList'}
    for object in objects:
        list[object.id] = object.name
    return list


def messagelist(id):
    objects = Message.objects.filter(room_id=id)
    name = Chatroom.objects.get(id=id).name
    list = {'MessageList': name}
    for object in objects:
        message = {object.author.name: object.text}
        list[object.id] = message
    return list


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'соединение установлено'}))
        async_to_sync(self.channel_layer.group_add)("all_instructions", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_instructions", self.channel_name)

    def all_user(self, text_data=None):
        message = text_data
        print('order for all users:', message)
        if message['order'] == "send_list_users":
            self.send(json.dumps(userlist()))
            print('новый список пользователей отправлен всем клиентам')
        if message['order'] == "send_list_rooms":
            self.send(json.dumps(roomlist()))
            print('новый список чатов отправлен всем клиентам')

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        print('incoming path:', self.scope["path"])
        print('incoming instructions message:', message)

        if 'load' in message:
            if message['load'] == "users":
                self.send(json.dumps(userlist()))
                print('список пользователей отправлен клиенту')
            if message['load'] == 'rooms':
                self.send(json.dumps(roomlist()))
                print('список чатов отправлен клиенту')
            if message['load'] == 'messageList':
                self.send(json.dumps(messagelist(message['newroom_id'])))
                print('список сообщений комнаты ID:', message['newroom_id'], 'отправлен клиенту')

        if 'create_user' in message:
            name = message['create_user']
            if not Profile.objects.filter(name=name).exists():
                user = Profile(name=name)
                user.save()
                print('новый пользователь', name, "создан")
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})
            else:
                self.send(json.dumps({'message': 'Пользователь уже существует'}))
                print('Пользователь уже существует')

        if 'create_room' in message:
            name = message['create_room']
            if not Chatroom.objects.filter(name=name).exists():
                room = Chatroom(name=name)
                room.save()
                print('новый чат', name, "создан")
                async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
            else:
                self.send(json.dumps({'message': 'Чат уже существует'}))
                print('Чат уже существует')

        if 'delete_user' in message:
            id = message['delete_user']
            user = Profile.objects.get(id=id)
            user.delete()
            print('ID пользователя', id, "удален")
            async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})

        if 'delete_room' in message:
            id = message['delete_room']
            room = Chatroom.objects.get(id=id)
            room.delete()
            print('ID чата', id, "удален")
            async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})

        if 'order' in message:
            if message['order'] == 'changeUserName':
                id = message['id']
                name = message['name']
                if not Profile.objects.filter(name=name).exists():
                    user = Profile.objects.get(id=id)
                    user.name = name
                    user.save()
                    print('Имя пользователя ID:', id, 'изменено на:', name)
                    async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_users"})
                else:
                    self.send(json.dumps({'message': 'Пользователь уже существует'}))
                    print('Пользователь уже существует')

            if message['order'] == 'changeRoomName':
                id = message['id']
                name = message['name']
                if not Chatroom.objects.filter(name=name).exists():
                    room = Chatroom.objects.get(id=id)
                    room.name = name
                    room.save()
                    print('Имя чата с ID:', id, 'изменено на:', name)
                    async_to_sync(self.channel_layer.group_send)("all_instructions", {"type": "all_user", "order": "send_list_rooms"})
                else:
                    self.send(json.dumps({'message': 'Чат уже существует'}))
                    print('Чат уже существует')


class WSChat(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(json.dumps({'message': 'соединение c чатом установлено'}))
        async_to_sync(self.channel_layer.group_add)("all_chat", self.channel_name)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)("all_chat", self.channel_name)

    def incoming_message(self, text_data=None):
        message = text_data
        print('incoming message from group:', message)
        if message['order'] == "accept_message":
            name = message['name']
            message = message['message']
            self.send(json.dumps({'message': message, 'name': name}))
            print('сообщение принято')

    def all_chats(self, text_data=None):
        message = text_data
        print('incoming message from group:', message)

    def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        print('incoming path:', self.scope["path"])
        print('incoming instructions message:', message)

        if 'usersendcommandroom' in message:
            if message['usersendcommandroom'] == 'roomselect':
                if message['oldroom_id'] != '':
                    oldroom_id = str(message['oldroom_id'])
                    async_to_sync(self.channel_layer.group_discard)(oldroom_id, self.channel_name)
                    print('Произошло отключение от чата', oldroom_id)
                newroom_id = str(message['newroom_id'])
                async_to_sync(self.channel_layer.group_add)(newroom_id, self.channel_name)
                print('Произошло подключение к чату', newroom_id)

            if message['usersendcommandroom'] == 'message':
                room_id = str(message['room_id'])
                user_id = message['userid']
                username = Profile.objects.get(id=user_id).name
                message = message['message']
                message_save = Message(author=Profile.objects.get(id=user_id), room=Chatroom.objects.get(id=room_id), text=message)
                message_save.save()
                print('Сообщение', message, 'сохранено')
                async_to_sync(self.channel_layer.group_send)(room_id, {"type": "incoming_message", "order": "accept_message", "name": username, "message": message})
                print('Сообщение', message, 'отправлено в чат', room_id)