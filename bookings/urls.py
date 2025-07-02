from django.urls import path
from .views import BookingCreateView, MpesaPaymentView, DailyRoomPriceListAPIView, MpesaSTKPushView, mpesa_callback, PaymentHistoryAPIView

urlpatterns = [
    path('bookings/', BookingCreateView.as_view(), name='booking-create'),
    path('mpesa/pay/', MpesaPaymentView.as_view(), name='mpesa-pay'),
    path('daily-prices/', DailyRoomPriceListAPIView.as_view(), name='daily-room-prices'),
    path('mpesa/stkpush/', MpesaSTKPushView.as_view(), name='mpesa-stkpush'),
    path('mpesa/callback/', mpesa_callback, name='mpesa-callback'),
    path('payments/', PaymentHistoryAPIView.as_view(), name='payment-history'),
]