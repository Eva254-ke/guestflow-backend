from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Booking, Payment, DailyRoomPrice, ExchangeRate
from rentals.models import Room

class HotelScopedAdmin(admin.ModelAdmin):
    """Base admin class that filters data by hotel for non-superusers"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        elif hasattr(request.user, 'hotel') and request.user.hotel:
            # Filter by hotel for hotel admins/staff
            if hasattr(qs.model, 'hotel'):
                return qs.filter(hotel=request.user.hotel)
            elif hasattr(qs.model, 'room__hotel'):
                return qs.filter(room__hotel=request.user.hotel)
            elif hasattr(qs.model, 'booking__hotel'):
                return qs.filter(booking__hotel=request.user.hotel)
        return qs.none()

@admin.register(Booking)
class BookingAdmin(HotelScopedAdmin):
    list_display = [
        'booking_reference', 'get_hotel', 'guest_name', 'room', 
        'check_in_date', 'check_out_date', 'nights', 'total_amount', 
        'get_status_badge', 'created_at'
    ]
    list_filter = [
        'hotel', 'status', 'source', 'check_in_date', 
        'check_out_date', 'created_at'
    ]
    search_fields = [
        'booking_reference', 'guest_name', 'guest_email', 
        'guest_phone', 'guest__username', 'guest__email'
    ]
    readonly_fields = [
        'id', 'booking_reference', 'nights', 'subtotal', 
        'total_amount', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('id', 'booking_reference', 'hotel', 'room', 'status', 'source')
        }),
        ('Guest Information', {
            'fields': ('guest', 'guest_name', 'guest_email', 'guest_phone', 'guest_address', 'guest_id_number')
        }),
        ('Stay Details', {
            'fields': ('check_in_date', 'check_out_date', 'nights', 'adults', 'children', 'infants')
        }),
        ('Pricing', {
            'fields': ('room_rate', 'subtotal', 'tax_amount', 'fee_amount', 'discount_amount', 'total_amount', 'currency')
        }),
        ('Additional Information', {
            'fields': ('special_requests', 'internal_notes')
        }),
        ('Check-in/out Details', {
            'fields': ('actual_check_in', 'actual_check_out', 'checked_in_by', 'checked_out_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'cancelled_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_hotel(self, obj):
        if obj.hotel:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:users_hotel_change', args=[obj.hotel.id]),
                obj.hotel.name
            )
        return "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'hotel__name'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'confirmed': '#28a745',
            'checked_in': '#17a2b8',
            'checked_out': '#6c757d',
            'cancelled': '#dc3545',
            'no_show': '#fd7e14',
            'refunded': '#6f42c1'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin'):
                if hasattr(request.user, 'hotel') and request.user.hotel:
                    kwargs["queryset"] = Room.objects.filter(hotel=request.user.hotel)
        elif db_field.name == "hotel":
            if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin'):
                if hasattr(request.user, 'hotel') and request.user.hotel:
                    kwargs["queryset"] = request.user.hotel.__class__.objects.filter(id=request.user.hotel.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Payment)
class PaymentAdmin(HotelScopedAdmin):
    list_display = [
        'get_booking_ref', 'get_hotel', 'amount', 'currency',
        'payment_method', 'get_status_badge', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = [
        'booking__booking_reference', 'transaction_id', 
        'reference_number', 'booking__guest_name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'booking', 'user', 'amount', 'currency', 'payment_method', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'reference_number', 'gateway_response')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_booking_ref(self, obj):
        if obj.booking:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:bookings_booking_change', args=[obj.booking.id]),
                obj.booking.booking_reference
            )
        return "No Booking"
    get_booking_ref.short_description = 'Booking Reference'
    get_booking_ref.admin_order_field = 'booking__booking_reference'
    
    def get_hotel(self, obj):
        if obj.booking and obj.booking.hotel:
            return obj.booking.hotel.name
        return "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'booking__hotel__name'
    
    def get_status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'completed': '#28a745',
            'failed': '#dc3545',
            'cancelled': '#6c757d',
            'refunded': '#fd7e14',
            'partially_refunded': '#e83e8c'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'

@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate', 'date']
    list_filter = ['from_currency', 'to_currency', 'date']
    search_fields = ['from_currency', 'to_currency']
    ordering = ['-date', 'from_currency']

@admin.register(DailyRoomPrice)
class DailyRoomPriceAdmin(HotelScopedAdmin):
    list_display = ['room', 'get_hotel', 'date', 'price', 'currency', 'is_available']
    list_filter = ['room__hotel', 'date', 'currency', 'is_available']
    search_fields = ['room__name', 'room__hotel__name']
    ordering = ['room', 'date']
    
    def get_hotel(self, obj):
        return obj.room.hotel.name if obj.room and obj.room.hotel else "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'room__hotel__name'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin'):
                if hasattr(request.user, 'hotel') and request.user.hotel:
                    kwargs["queryset"] = Room.objects.filter(hotel=request.user.hotel)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)