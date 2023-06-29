from .views import UsersApi, RoomsApi
from rest_framework.routers import DefaultRouter
from django.urls import path, include


router = DefaultRouter()
router.register('rooms', RoomsApi)
router.register('users', UsersApi)

urlpatterns = [
    path('api/', include(router.urls)),
]
