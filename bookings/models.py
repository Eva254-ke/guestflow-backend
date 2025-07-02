from django.db import models
from django.contrib.auth import get_user_model
from rentals.models import Room, Hotel
from django.core.validators import MinValueValidator
import uuid
from datetime import datetime, timedelta

User = get_user_model()

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
        ('refunded', 'Refunded'),
    ]
    
    BOOKING_SOURCE = [
        ('direct', 'Direct Booking'),
        ('website', 'Website'),
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('walk_in', 'Walk-in'),
        ('agent', 'Travel Agent'),
        ('booking_com', 'Booking.com'),
        ('airbnb', 'Airbnb'),
        ('expedia', 'Expedia'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=20, unique=True, help_text="Unique booking reference")
    
    # Relationships
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    
    # Guest Information (for non-registered users)
    guest_name = models.CharField(max_length=200, help_text="Primary guest name")
    guest_email = models.EmailField(help_text="Guest email address")
    guest_phone = models.CharField(max_length=20, help_text="Guest phone number")
    guest_address = models.TextField(blank=True, help_text="Guest address")
    guest_id_number = models.CharField(max_length=50, blank=True, help_text="Guest ID/Passport number")
    
    # Stay Details
    check_in_date = models.DateField(help_text="Check-in date")
    check_out_date = models.DateField(help_text="Check-out date")
    nights = models.PositiveIntegerField(help_text="Number of nights")
    
    # Guest Count
    adults = models.PositiveIntegerField(default=1, help_text="Number of adults")
    children = models.PositiveIntegerField(default=0, help_text="Number of children")
    infants = models.PositiveIntegerField(default=0, help_text="Number of infants")
    
    # Pricing
    room_rate = models.DecimalField(max_digits=10, decimal_places=2, help_text="Room rate per night")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, help_text="Subtotal before taxes and fees")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total tax amount")
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Total fee amount")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Discount amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total amount to pay")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code")
    
    # Booking Details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    source = models.CharField(max_length=20, choices=BOOKING_SOURCE, default='direct')
    special_requests = models.TextField(blank=True, help_text="Special requests from guest")
    internal_notes = models.TextField(blank=True, help_text="Internal notes (not visible to guest)")
    
    # Check-in/out Details
    actual_check_in = models.DateTimeField(null=True, blank=True, help_text="Actual check-in time")
    actual_check_out = models.DateTimeField(null=True, blank=True, help_text="Actual check-out time")
    checked_in_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_in_bookings')
    checked_out_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='checked_out_bookings')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        indexes = [
            models.Index(fields=['hotel', 'status']),
            models.Index(fields=['check_in_date', 'check_out_date']),
            models.Index(fields=['booking_reference']),
            models.Index(fields=['guest_email']),
        ]
    
    def __str__(self):
        return f"{self.booking_reference} - {self.guest_name} ({self.room.name})"
    
    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = self.generate_booking_reference()
        
        # Calculate nights
        if self.check_in_date and self.check_out_date:
            self.nights = (self.check_out_date - self.check_in_date).days
        
        # Calculate subtotal
        if self.room_rate and self.nights:
            self.subtotal = self.room_rate * self.nights
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount + self.fee_amount - self.discount_amount
        
        # Auto-assign hotel from room
        if self.room and not self.hotel_id:
            self.hotel = self.room.hotel
        
        super().save(*args, **kwargs)
    
    def generate_booking_reference(self):
        """Generate unique booking reference"""
        import string
        import random
        
        prefix = self.hotel.property_type.upper()[:2] if self.hotel else 'BK'
        timestamp = datetime.now().strftime('%Y%m%d')
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        return f"{prefix}{timestamp}{random_suffix}"
    
    @property
    def duration_text(self):
        """Return human-readable duration"""
        if self.nights == 1:
            return "1 night"
        return f"{self.nights} nights"
    
    @property
    def guest_count_text(self):
        """Return guest count as text"""
        parts = []
        if self.adults > 0:
            parts.append(f"{self.adults} adult{'s' if self.adults > 1 else ''}")
        if self.children > 0:
            parts.append(f"{self.children} child{'ren' if self.children > 1 else ''}")
        if self.infants > 0:
            parts.append(f"{self.infants} infant{'s' if self.infants > 1 else ''}")
        return ', '.join(parts)
    
    def can_cancel(self):
        """Check if booking can be cancelled"""
        return self.status in ['pending', 'confirmed']
    
    def can_check_in(self):
        """Check if guest can check in"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.status == 'confirmed' and self.check_in_date <= today
    
    def can_check_out(self):
        """Check if guest can check out"""
        return self.status == 'checked_in'

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('mpesa', 'M-Pesa'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('flutterwave', 'Flutterwave'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Payment Details
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Payment amount")
    currency = models.CharField(max_length=3, default='USD')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, blank=True, help_text="External transaction ID")
    reference_number = models.CharField(max_length=100, blank=True, help_text="Payment reference number")
    gateway_response = models.TextField(blank=True, help_text="Payment gateway response")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.amount} {self.currency} for {self.booking.booking_reference}"

class ExchangeRate(models.Model):
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_currency', 'to_currency', 'date']
    
    def __str__(self):
        return f"{self.from_currency} to {self.to_currency}: {self.rate}"

class DailyRoomPrice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='daily_prices')
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['room', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.room.name} - {self.date}: {self.price} {self.currency}"