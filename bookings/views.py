import os
import base64
import requests
from datetime import datetime, timedelta
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.dateparse import parse_date
from .models import Booking, Payment, DailyRoomPrice, ExchangeRate
from .serializers import BookingSerializer, PaymentSerializer, DailyRoomPriceSerializer
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from rentals.models import Room

class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

class MpesaPaymentView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Logic for M-Pesa STK Push goes here
        serializer.save()

class BookingCreateAPIView(APIView):
    def post(self, request):
        return Response({'detail': 'Not implemented'}, status=501)

class DailyRoomPriceListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        room_id = request.query_params.get('room_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        # --- Debug log for production readiness ---
        import logging
        logger = logging.getLogger('django')
        logger.info(f"DailyRoomPriceListAPIView: room_id={room_id}, start_date={start_date}, end_date={end_date}")
        if not (room_id and start_date and end_date):
            return Response({'detail': 'room_id, start_date, and end_date are required.'}, status=400)
        try:
            start = parse_date(start_date)
            end = parse_date(end_date)
        except Exception:
            return Response({'detail': 'Invalid date format.'}, status=400)
        # Fetch all prices in range
        prices = DailyRoomPrice.objects.filter(room_id=room_id, date__range=[start, end])
        price_map = {p.date: p for p in prices}
        # Get the room base price
        from rentals.models import Room
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'detail': 'Room not found.'}, status=404)
        # Get the latest exchange rate for the room's rental
        try:
            exchange_rate = ExchangeRate.objects.get(rental=room.rental)
            rate = float(exchange_rate.rate)
        except ExchangeRate.DoesNotExist:
            rate = None
        # Generate all dates in range
        days = (end - start).days + 1
        result = []
        for i in range(days):
            day = start + timedelta(days=i)
            price_obj = price_map.get(day)
            if price_obj:
                # Use serializer for existing price
                data = DailyRoomPriceSerializer(price_obj).data
            else:
                # Convert base price from KES to USD if rate is available
                if rate and rate > 0:
                    usd_price = float(room.base_price) / rate
                    usd_price = round(usd_price, 2)
                else:
                    usd_price = float(room.base_price)
                data = {
                    'id': None,
                    'room': int(room_id),
                    'date': day.isoformat(),
                    'price': str(usd_price),  # USD
                    'rate_used': str(rate) if rate else None
                }
            result.append(data)
        return Response(result)

class MpesaSTKPushView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Debug: Log environment variables for troubleshooting
        import logging
        logger = logging.getLogger('django')
        logger.info(f"MPESA_CONSUMER_KEY (os.environ)={os.environ.get('MPESA_CONSUMER_KEY')}")
        logger.info(f"MPESA_CONSUMER_KEY (settings)={getattr(settings, 'MPESA_CONSUMER_KEY', None)}")
        logger.info(f"MPESA_CONSUMER_SECRET (os.environ)={os.environ.get('MPESA_CONSUMER_SECRET')}")
        logger.info(f"MPESA_CONSUMER_SECRET (settings)={getattr(settings, 'MPESA_CONSUMER_SECRET', None)}")
        logger.info(f"MPESA_PASSKEY (os.environ)={os.environ.get('MPESA_PASSKEY')}")
        logger.info(f"MPESA_PASSKEY (settings)={getattr(settings, 'MPESA_PASSKEY', None)}")
        logger.info(f"MPESA_SHORTCODE (os.environ)={os.environ.get('MPESA_SHORTCODE')}")
        logger.info(f"MPESA_SHORTCODE (settings)={getattr(settings, 'MPESA_SHORTCODE', None)}")
        logger.info(f"MPESA_CALLBACK_URL (os.environ)={os.environ.get('MPESA_CALLBACK_URL')}")
        logger.info(f"MPESA_CALLBACK_URL (settings)={getattr(settings, 'MPESA_CALLBACK_URL', None)}")
        # Get payment details from request
        phone = request.data.get('phone')
        amount = request.data.get('amount')
        account_ref = request.data.get('account_ref', 'Booking')
        transaction_desc = request.data.get('transaction_desc', 'Hotel Booking')
        rental_slug = request.data.get('rental_slug')
        room_id = request.data.get('room_id')
        user = request.user if request.user.is_authenticated else None

        if not phone or not amount or not rental_slug or not room_id:
            return Response({'error': 'phone, amount, rental_slug, and room_id are required.'}, status=400)

        # Get M-Pesa credentials from Django settings (preferred)
        MPESA_CONSUMER_KEY = getattr(settings, 'MPESA_CONSUMER_KEY', None)
        MPESA_CONSUMER_SECRET = getattr(settings, 'MPESA_CONSUMER_SECRET', None)
        MPESA_SHORTCODE = getattr(settings, 'MPESA_SHORTCODE', '174379')
        MPESA_PASSKEY = getattr(settings, 'MPESA_PASSKEY', None)
        MPESA_CALLBACK_URL = getattr(settings, 'MPESA_CALLBACK_URL', 'https://yourdomain.com/api/mpesa-callback/')
        if not (MPESA_CONSUMER_KEY and MPESA_CONSUMER_SECRET and MPESA_PASSKEY):
            return Response({'error': 'M-Pesa credentials not set.'}, status=500)

        # Generate timestamp and password
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode()

        # Get access token
        try:
            token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
            r = requests.get(token_url, auth=(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
            r.raise_for_status()
            access_token = r.json()['access_token']
        except Exception as e:
            return Response({'error': f'Failed to get access token: {str(e)}'}, status=500)

        # Prepare STK Push payload
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": str(amount),
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": account_ref[:12],
            "TransactionDesc": transaction_desc[:13]
        }
        logger.info(f"STK Push Payload: {payload}")
        logger.info(f"STK Push Headers: {headers}")
        try:
            response = requests.post(
                'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                json=payload, headers=headers, timeout=15
            )
            logger.info(f"STK Push Response Status: {response.status_code}")
            logger.info(f"STK Push Response Body: {response.text}")
            response.raise_for_status()
            resp_json = response.json()
        except Exception as e:
            return Response({'error': f'STK Push failed: {str(e)}', 'safaricom_response': getattr(e, 'response', None) and e.response.text}, status=500)

        # Optionally, log or save the payment initiation for this rental/room/user
        # You can create a Payment object here with status 'pending'
        Payment.objects.create(
            user=user,
            room_id=room_id,
            rental_slug=rental_slug,
            phone=phone,
            amount=amount,
            status='pending',
            mpesa_merchant_request_id=resp_json.get('MerchantRequestID'),
            mpesa_checkout_request_id=resp_json.get('CheckoutRequestID'),
            response=resp_json
        )
        return Response(resp_json, status=response.status_code)

# Callback endpoint for M-Pesa
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def mpesa_callback(request):
    # Save or process the callback data as needed
    import logging
    logger = logging.getLogger('django')
    logger.info(f"M-Pesa Callback: {request.data}")
    # Find the Payment by CheckoutRequestID and update status
    callback = request.data.get('Body', {}).get('stkCallback', {})
    checkout_id = callback.get('CheckoutRequestID')
    result_code = callback.get('ResultCode')
    result_desc = callback.get('ResultDesc')
    payment = Payment.objects.filter(mpesa_checkout_request_id=checkout_id).first()
    if payment:
        payment.status = 'paid' if result_code == 0 else 'failed'
        payment.response = callback
        payment.save()
    return Response({'result': 'Callback received'}, status=200)

class PaymentHistoryAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all().order_by('-timestamp')
        return Payment.objects.filter(user=user).order_by('-timestamp')