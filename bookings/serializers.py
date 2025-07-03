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
        fields = ['id', 'from_currency', 'to_currency', 'rate', 'date']

class DailyRoomPriceSerializer(serializers.ModelSerializer):
    rate_used = serializers.SerializerMethodField()

    class Meta:
        model = DailyRoomPrice
        fields = ['id', 'room', 'date', 'price', 'rate_used']

    def get_rate_used(self, obj):
        # Assumes obj has a rate_used attribute or property set in the queryset or view
        return getattr(obj, 'rate_used', None)