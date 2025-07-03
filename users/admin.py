from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import Hotel, CustomUser, UserToken

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'property_type', 'city', 'country', 
        'rating', 'get_staff_count', 'get_rooms_count', 
        'get_status_badges', 'created_at'
    ]
    list_filter = [
        'property_type', 'is_active', 'is_verified', 
        'is_featured', 'city', 'country', 'star_rating'
    ]
    search_fields = ['name', 'email', 'city', 'address', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_rooms']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'property_type', 'short_description')
        }),
        ('Contact Details', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state_province', 'postal_code', 'country', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('description', 'logo', 'cover_image', 'amenities', 'languages_spoken')
        }),
        ('Business Information', {
            'fields': ('check_in_time', 'check_out_time', 'cancellation_policy')
        }),
        ('Ratings & Reviews', {
            'fields': ('star_rating', 'rating', 'total_reviews')
        }),
        ('Status', {
            'fields': ('is_active', 'is_verified', 'is_featured')
        }),
        ('Meta Information', {
            'fields': ('id', 'created_at', 'updated_at', 'total_rooms'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        elif hasattr(request.user, 'hotel') and request.user.hotel:
            return qs.filter(id=request.user.hotel.id)
        return qs.none()
    
    def get_staff_count(self, obj):
        staff_count = obj.staff_members.filter(is_active=True).count()
        return format_html(
            '<a href="{}?hotel__id__exact={}">{} staff</a>',
            reverse('admin:users_customuser_changelist'),
            obj.id,
            staff_count
        )
    get_staff_count.short_description = 'Staff'
    
    def get_rooms_count(self, obj):
        rooms_count = obj.rooms.filter(is_active=True).count()
        if rooms_count > 0:
            return format_html(
                '<a href="{}?hotel__id__exact={}">{} rooms</a>',
                reverse('admin:rentals_room_changelist'),
                obj.id,
                rooms_count
            )
        return "0 rooms"
    get_rooms_count.short_description = 'Rooms'
    
    def get_status_badges(self, obj):
        badges = []
        
        if obj.is_active:
            badges.append('<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 5px;">ACTIVE</span>')
        else:
            badges.append('<span style="background-color: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 5px;">INACTIVE</span>')
        
        if obj.is_verified:
            badges.append('<span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 5px;">VERIFIED</span>')
        
        if obj.is_featured:
            badges.append('<span style="background-color: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 5px;">FEATURED</span>')
        
        return format_html(''.join(badges))
    get_status_badges.short_description = 'Status'

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = [
        'username', 'get_full_name', 'email', 'get_role_badge', 
        'hotel', 'phone', 'get_verification_status', 'is_active', 'created_at'
    ]
    list_filter = [
        'role', 'is_active', 'is_verified', 'phone_verified',
        'hotel', 'gender', 'preferred_language', 'receive_notifications'
    ]
    search_fields = [
        'username', 'email', 'first_name', 'last_name', 
        'phone', 'hotel__name'
    ]
    ordering = ['username']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'last_login_ip',
        'date_joined', 'last_login'
    ]
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Hotel Association', {
            'fields': ('role', 'hotel')
        }),
        ('Extended Profile', {
            'fields': ('phone', 'address', 'city', 'country', 'postal_code')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'profile_picture', 'bio')
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'preferred_currency', 'receive_notifications', 'receive_marketing')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'phone_verified')
        }),
        ('System Information', {
            'fields': ('id', 'created_at', 'updated_at', 'last_login_ip'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role & Hotel Association', {
            'fields': ('role', 'hotel')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        elif getattr(request.user, 'role', None) == 'hotel_admin' and hasattr(request.user, 'hotel') and request.user.hotel:
            # Hotel admins can see their hotel staff and customers who booked with them
            return qs.filter(
                models.Q(hotel=request.user.hotel) |
                models.Q(bookings__hotel=request.user.hotel)
            ).distinct()
        elif getattr(request.user, 'role', None) == 'hotel_staff' and hasattr(request.user, 'hotel') and request.user.hotel:
            # Hotel staff can only see customers who booked with their hotel
            return qs.filter(bookings__hotel=request.user.hotel).distinct()
        return qs.filter(id=request.user.id)
    
    def get_role_badge(self, obj):
        role_info = obj.get_role_display_badge()
        return format_html(
            '<span class="badge {}">{}</span>',
            role_info['class'],
            role_info['text']
        )
    get_role_badge.short_description = 'Role'
    get_role_badge.admin_order_field = 'role'
    
    def get_verification_status(self, obj):
        badges = []
        
        if obj.is_verified:
            badges.append('<span style="background-color: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 3px;">EMAIL</span>')
        
        if obj.phone_verified:
            badges.append('<span style="background-color: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin-right: 3px;">PHONE</span>')
        
        if not badges:
            badges.append('<span style="background-color: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 10px;">PENDING</span>')
        
        return format_html(''.join(badges))
    get_verification_status.short_description = 'Verified'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "hotel":
            if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin'):
                if hasattr(request.user, 'hotel') and request.user.hotel:
                    kwargs["queryset"] = Hotel.objects.filter(id=request.user.hotel.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        if obj is None:
            return True
        
        # Super admins can edit anyone
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return True
        
        # Hotel admins can edit their hotel staff and customers
        if getattr(request.user, 'role', None) == 'hotel_admin':
            if hasattr(request.user, 'hotel') and request.user.hotel:
                return (obj.hotel == request.user.hotel or 
                       obj.bookings.filter(hotel=request.user.hotel).exists())
        
        # Users can edit themselves
        return obj == request.user
    
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            return False
        
        # Super admins can delete anyone except themselves
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return obj != request.user
        
        # Hotel admins can delete their hotel staff (not customers)
        if getattr(request.user, 'role', None) == 'hotel_admin':
            if hasattr(request.user, 'hotel') and request.user.hotel:
                return (obj.hotel == request.user.hotel and 
                       obj.role in ['hotel_staff'] and 
                       obj != request.user)
        
        return False

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'token_type', 'get_token_preview', 
        'is_active', 'get_expiry_status', 'created_at', 'last_used'
    ]
    list_filter = ['token_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'last_used']
    
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token', 'token_type', 'is_active')
        }),
        ('Expiry & Usage', {
            'fields': ('expires_at', 'created_at', 'last_used')
        })
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, 'role', None) == 'super_admin':
            return qs
        elif getattr(request.user, 'role', None) in ['hotel_admin', 'hotel_staff']:
            if hasattr(request.user, 'hotel') and request.user.hotel:
                return qs.filter(user__hotel=request.user.hotel)
        return qs.filter(user=request.user)
    
    def get_token_preview(self, obj):
        if obj.token:
            return f"{obj.token[:8]}...{obj.token[-4:]}"
        return "No Token"
    get_token_preview.short_description = 'Token Preview'
    
    def get_expiry_status(self, obj):
        if not obj.expires_at:
            return format_html('<span style="color: #28a745;">Never Expires</span>')
        elif obj.is_expired:
            return format_html('<span style="color: #dc3545;">Expired</span>')
        else:
            return format_html('<span style="color: #ffc107;">Valid</span>')
    get_expiry_status.short_description = 'Expiry Status'

# Import models for the signal to work
from django.db import models

# Customize admin site header and title
admin.site.site_header = "GuestFlow Administration"
admin.site.site_title = "GuestFlow Admin"
admin.site.index_title = "Welcome to GuestFlow Administration"
admin.site.register(CustomUser, CustomUserAdmin)
