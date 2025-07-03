from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Rental, Room  # Removed PriceOverride
from .serializers import RoomSerializer
from bookings.models import Booking, DailyRoomPrice
from datetime import datetime, timedelta
from decimal import Decimal
from rest_framework.permissions import AllowAny

# Any logic using PriceOverride should be migrated to use DailyRoomPrice from bookings.models

class RoomListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, slug):
        checkin = request.GET.get('checkin')
        checkout = request.GET.get('checkout')
        rental = get_object_or_404(Rental, slug=slug)
        rooms = rental.rooms.all()
        # If no dates provided, return all rooms
        if not checkin or not checkout:
            serializer = RoomSerializer(rooms, many=True, context={'request': request})
            return Response(serializer.data)
        try:
            checkin_date = datetime.strptime(checkin, "%Y-%m-%d").date()
            checkout_date = datetime.strptime(checkout, "%Y-%m-%d").date()
        except ValueError:
            return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        if checkin_date >= checkout_date:
            return Response({'detail': 'Checkout must be after checkin.'}, status=status.HTTP_400_BAD_REQUEST)
        available_rooms = []
        for room in rooms:
            overlapping = Booking.objects.filter(
                room=room,
                check_in_date__lt=checkout_date,
                check_out_date__gt=checkin_date,
                status__in=['pending', 'paid']
            ).exists()
            if not overlapping:
                total_price = Decimal('0.00')
                nights = (checkout_date - checkin_date).days
                price_breakdown = []
                for i in range(nights):
                    day = checkin_date + timedelta(days=i)
                    daily_price_obj = DailyRoomPrice.objects.filter(room=room, date=day).first()
                    if daily_price_obj:
                        total_price += daily_price_obj.price
                        price_breakdown.append({'date': str(day), 'price': float(daily_price_obj.price)})
                    else:
                        total_price += room.base_price
                        price_breakdown.append({'date': str(day), 'price': float(room.base_price)})
                # Add fees and taxes using Decimal
                fees = list(room.fees.values('name', 'amount'))
                taxes = list(room.taxes.values('name', 'rate'))
                fees_total = sum(Decimal(str(f['amount'])) for f in fees)
                taxes_total = sum(Decimal(str(t['rate'])) for t in taxes)
                total_amount = total_price + fees_total + taxes_total
                room_data = RoomSerializer(room, context={'request': request}).data
                room_data['total_price'] = float(total_amount)
                room_data['nights'] = nights
                room_data['price_breakdown'] = price_breakdown
                room_data['fees'] = fees
                room_data['taxes'] = taxes
                available_rooms.append(room_data)
        return Response(available_rooms)