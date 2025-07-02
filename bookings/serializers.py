from rest_framework import serializers
from .models import Booking, Payment, DailyRoomPrice, ExchangeRate

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['id', 'rental', 'rate', 'updated_at']

class DailyRoomPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRoomPrice
        fields = ['id', 'room', 'date', 'price', 'rate_used']