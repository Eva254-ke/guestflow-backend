from django.urls import path
from .views import RoomListAPIView

urlpatterns = [
    path('<slug:slug>/rooms/', RoomListAPIView.as_view(), name='room-list'),
]