from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .mongo_models import HotelDocument, RoomDocument, BookingDocument, ReviewDocument

class MongoAdminMixin:
    """Mixin for MongoDB document admin"""
    
    def has_add_permission(self, request):
        return request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff
    
    def get_queryset(self, request):
        """Filter based on user permissions"""
        if request.user.is_superuser:
            return self.model.objects.all()
        elif hasattr(request.user, 'hotel') and request.user.hotel:
            # Filter by hotel for hotel admins
            if hasattr(self.model, 'hotel_id'):
                # For rooms, bookings, reviews
                hotel_docs = HotelDocument.objects.filter(owner_id=request.user.id)
                hotel_ids = [hotel.id for hotel in hotel_docs]
                return self.model.objects.filter(hotel_id__in=hotel_ids)
            elif hasattr(self.model, 'owner_id'):
                # For hotels
                return self.model.objects.filter(owner_id=request.user.id)
        return self.model.objects.none()

@admin.register(HotelDocument)
class HotelDocumentAdmin(admin.ModelAdmin, MongoAdminMixin):
    list_display = ['name', 'property_type', 'city', 'country', 'rating', 'is_active', 'created_at']
    list_filter = ['property_type', 'city', 'country', 'is_active']
    search_fields = ['name', 'city', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'property_type', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country', 'latitude', 'longitude')
        }),
        ('Business Details', {
            'fields': ('rating', 'total_reviews', 'check_in_time', 'check_out_time')
        }),
        ('Media & Features', {
            'fields': ('logo_url', 'images', 'amenities', 'rules')
        }),
        ('System Fields', {
            'fields': ('owner_id', 'is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            obj.owner_id = request.user.id
        super().save_model(request, obj, form, change)

@admin.register(RoomDocument)
class RoomDocumentAdmin(admin.ModelAdmin, MongoAdminMixin):
    list_display = ['name', 'get_hotel_name', 'room_type', 'capacity', 'base_price', 'currency', 'is_available']
    list_filter = ['room_type', 'capacity', 'is_available', 'currency']
    search_fields = ['name', 'room_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('hotel_id', 'name', 'room_type', 'room_number', 'description')
        }),
        ('Capacity & Beds', {
            'fields': ('capacity', 'size_sqm', 'bed_type', 'bed_count')
        }),
        ('Pricing', {
            'fields': ('base_price', 'currency', 'weekend_multiplier', 'seasonal_rates')
        }),
        ('Features & Amenities', {
            'fields': ('amenities', 'features', 'images')
        }),
        ('Availability', {
            'fields': ('is_available', 'maintenance_mode')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_hotel_name(self, obj):
        try:
            hotel = HotelDocument.objects.get(id=obj.hotel_id)
            return hotel.name
        except:
            return "Unknown Hotel"
    get_hotel_name.short_description = 'Hotel'

@admin.register(BookingDocument)
class BookingDocumentAdmin(admin.ModelAdmin, MongoAdminMixin):
    list_display = [
        'booking_reference', 'get_hotel_name', 'get_room_name', 
        'guest_name', 'check_in_date', 'check_out_date', 
        'status', 'total_amount', 'currency'
    ]
    list_filter = ['status', 'check_in_date', 'payment_status', 'currency']
    search_fields = ['booking_reference', 'guest_name', 'guest_email', 'guest_phone']
    readonly_fields = ['booking_reference', 'nights', 'created_at', 'updated_at']
    date_hierarchy = 'check_in_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_reference', 'hotel_id', 'room_id', 'guest_user_id')
        }),
        ('Dates & Guests', {
            'fields': ('check_in_date', 'check_out_date', 'nights', 'guests_count')
        }),
        ('Guest Information', {
            'fields': ('guest_name', 'guest_email', 'guest_phone', 'guest_address', 'special_requests')
        }),
        ('Pricing', {
            'fields': ('room_rate', 'total_amount', 'taxes', 'fees', 'currency')
        }),
        ('Status & Timeline', {
            'fields': (
                'status', 'confirmed_at', 'checked_in_at', 'checked_out_at',
                'cancelled_at', 'cancellation_reason'
            )
        }),
        ('Payment', {
            'fields': ('payment_status', 'payment_method', 'payment_reference')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at', 'created_by_user_id'),
            'classes': ('collapse',)
        }),
    )
    
    def get_hotel_name(self, obj):
        try:
            hotel = HotelDocument.objects.get(id=obj.hotel_id)
            return hotel.name
        except:
            return "Unknown Hotel"
    get_hotel_name.short_description = 'Hotel'
    
    def get_room_name(self, obj):
        try:
            room = RoomDocument.objects.get(id=obj.room_id)
            return room.name
        except:
            return "Unknown Room"
    get_room_name.short_description = 'Room'

@admin.register(ReviewDocument)
class ReviewDocumentAdmin(admin.ModelAdmin, MongoAdminMixin):
    list_display = [
        'get_hotel_name', 'guest_name', 'rating', 'title', 
        'is_approved', 'is_featured', 'created_at'
    ]
    list_filter = ['rating', 'is_approved', 'is_featured', 'created_at']
    search_fields = ['guest_name', 'guest_email', 'title', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Review Information', {
            'fields': ('hotel_id', 'booking_id', 'guest_user_id')
        }),
        ('Guest Information', {
            'fields': ('guest_name', 'guest_email')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Detailed Ratings', {
            'fields': ('cleanliness_rating', 'service_rating', 'location_rating', 'value_rating')
        }),
        ('Status', {
            'fields': ('is_approved', 'is_featured')
        }),
        ('Hotel Response', {
            'fields': ('hotel_response', 'responded_at')
        }),
        ('System Fields', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_hotel_name(self, obj):
        try:
            hotel = HotelDocument.objects.get(id=obj.hotel_id)
            return hotel.name
        except:
            return "Unknown Hotel"
    get_hotel_name.short_description = 'Hotel'
