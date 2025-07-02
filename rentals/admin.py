from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Room, RoomImage, RoomPricing, RoomAvailability, Rental, RoomFee, RoomTax

class HotelScopedAdmin(admin.ModelAdmin):
    """Base admin class that filters data by hotel for non-superusers"""
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        elif hasattr(request.user, 'hotel') and request.user.hotel:
            if hasattr(qs.model, 'hotel'):
                return qs.filter(hotel=request.user.hotel)
            elif hasattr(qs.model, 'room__hotel'):
                return qs.filter(room__hotel=request.user.hotel)
        return qs.none()

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1
    fields = ['image', 'caption', 'alt_text', 'is_primary', 'order']
    ordering = ['-is_primary', 'order']

class RoomPricingInline(admin.TabularInline):
    model = RoomPricing
    extra = 1
    fields = ['pricing_type', 'price', 'currency', 'start_date', 'end_date', 'is_active']

class RoomFeeInline(admin.TabularInline):
    model = RoomFee
    extra = 1
    fields = ['name', 'amount', 'is_percentage', 'is_mandatory']

class RoomTaxInline(admin.TabularInline):
    model = RoomTax
    extra = 1
    fields = ['name', 'rate', 'is_inclusive']

@admin.register(Room)
class RoomAdmin(HotelScopedAdmin):
    list_display = [
        'name', 'get_hotel', 'room_type', 'max_occupancy', 
        'base_price', 'currency', 'get_availability_badge', 'created_at'
    ]
    list_filter = [
        'hotel', 'room_type', 'is_available', 'is_active',
        'bed_type', 'bathroom_type', 'has_wifi', 'has_ac'
    ]
    search_fields = ['name', 'hotel__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [RoomImageInline, RoomPricingInline, RoomFeeInline, RoomTaxInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'hotel', 'name', 'room_type', 'description', 'short_description')
        }),
        ('Capacity', {
            'fields': ('max_occupancy', 'adults', 'children', 'infants')
        }),
        ('Room Specifications', {
            'fields': ('size_sqm', 'bed_type', 'number_of_beds', 'bathroom_type')
        }),
        ('Amenities', {
            'fields': ('amenities', 'has_wifi', 'has_ac', 'has_tv', 'has_balcony', 'has_kitchen', 'has_parking')
        }),
        ('Pricing & Availability', {
            'fields': ('base_price', 'currency', 'is_available', 'min_stay', 'max_stay')
        }),
        ('Check-in/out Times', {
            'fields': ('check_in_time', 'check_out_time'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('is_active', 'created_at', 'updated_at'),
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
    
    def get_availability_badge(self, obj):
        if obj.is_available and obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Available</span>'
            )
        elif not obj.is_active:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Inactive</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-size: 11px;">Unavailable</span>'
            )
    get_availability_badge.short_description = 'Status'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hotel":
            if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin'):
                if hasattr(request.user, 'hotel') and request.user.hotel:
                    kwargs["queryset"] = request.user.hotel.__class__.objects.filter(id=request.user.hotel.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(RoomImage)
class RoomImageAdmin(HotelScopedAdmin):
    list_display = ['get_room_name', 'get_hotel', 'caption', 'is_primary', 'order', 'created_at']
    list_filter = ['room__hotel', 'is_primary']
    search_fields = ['room__name', 'caption', 'room__hotel__name']
    ordering = ['room', '-is_primary', 'order']
    
    def get_room_name(self, obj):
        return f"{obj.room.name}"
    get_room_name.short_description = 'Room'
    get_room_name.admin_order_field = 'room__name'
    
    def get_hotel(self, obj):
        return obj.room.hotel.name if obj.room and obj.room.hotel else "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'room__hotel__name'

@admin.register(RoomPricing)
class RoomPricingAdmin(HotelScopedAdmin):
    list_display = ['get_room_name', 'get_hotel', 'pricing_type', 'price', 'currency', 'start_date', 'end_date', 'is_active']
    list_filter = ['room__hotel', 'pricing_type', 'currency', 'is_active']
    search_fields = ['room__name', 'room__hotel__name']
    ordering = ['room', 'pricing_type']
    
    def get_room_name(self, obj):
        return f"{obj.room.name}"
    get_room_name.short_description = 'Room'
    get_room_name.admin_order_field = 'room__name'
    
    def get_hotel(self, obj):
        return obj.room.hotel.name if obj.room and obj.room.hotel else "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'room__hotel__name'

@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(HotelScopedAdmin):
    list_display = ['get_room_name', 'get_hotel', 'date', 'get_status_badge', 'price_override', 'notes']
    list_filter = ['room__hotel', 'status', 'date']
    search_fields = ['room__name', 'room__hotel__name', 'notes']
    ordering = ['room', 'date']
    
    def get_room_name(self, obj):
        return f"{obj.room.name}"
    get_room_name.short_description = 'Room'
    get_room_name.admin_order_field = 'room__name'
    
    def get_hotel(self, obj):
        return obj.room.hotel.name if obj.room and obj.room.hotel else "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'room__hotel__name'
    
    def get_status_badge(self, obj):
        colors = {
            'available': '#28a745',
            'booked': '#dc3545',
            'blocked': '#ffc107',
            'maintenance': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    get_status_badge.admin_order_field = 'status'

# Legacy Rental model admin
@admin.register(Rental)
class RentalAdmin(HotelScopedAdmin):
    list_display = ['title', 'get_hotel', 'owner', 'price_per_night', 'location', 'is_available']
    list_filter = ['hotel', 'is_available']
    search_fields = ['title', 'description', 'location']
    
    def get_hotel(self, obj):
        return obj.hotel.name if obj.hotel else "No Hotel"
    get_hotel.short_description = 'Hotel'
    get_hotel.admin_order_field = 'hotel__name'