from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rentals.views import RoomListAPIView
from bookings.views import BookingCreateAPIView, MpesaSTKPushView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rentals/<slug:slug>/rooms/', RoomListAPIView.as_view()),
    path('api/bookings/', BookingCreateAPIView.as_view()),
    path('api/mpesa/pay/', MpesaSTKPushView.as_view()),
    path('api/', include('bookings.urls')),
]

# Serve media files in both development and production (if needed)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
