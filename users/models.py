from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
import uuid

class Hotel(models.Model):
    PROPERTY_TYPES = [
        ('hotel', 'Hotel'),
        ('airbnb', 'Airbnb'),
        ('resort', 'Resort'),
        ('hostel', 'Hostel'),
        ('guesthouse', 'Guest House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
        ('motel', 'Motel'),
        ('boutique', 'Boutique Hotel'),
        ('lodge', 'Lodge'),
        ('inn', 'Inn'),
    ]
    
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, help_text="Name of the property")
    slug = models.SlugField(unique=True, max_length=220, help_text="URL-friendly name")
    property_type = models.CharField(
        max_length=20, 
        choices=PROPERTY_TYPES, 
        default='hotel',
        help_text="Type of accommodation"
    )
    
    # Contact Information
    email = models.EmailField(help_text="Primary contact email")
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+254712345678' or '0712345678'"
    )
    phone = models.CharField(validators=[phone_validator], max_length=17, help_text="Contact phone number")
    website = models.URLField(blank=True, help_text="Hotel website URL")
    
    # Location Information
    address = models.TextField(help_text="Full address of the property")
    city = models.CharField(max_length=100, db_index=True)
    state_province = models.CharField(max_length=100, blank=True, help_text="State or Province")
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, db_index=True)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
        help_text="Longitude coordinate"
    )
    
    # Property Details
    description = models.TextField(blank=True, help_text="Detailed description of the property")
    short_description = models.CharField(max_length=300, blank=True, help_text="Brief description for listings")
    logo = models.ImageField(upload_to='hotel_logos/', blank=True, null=True, help_text="Property logo")
    cover_image = models.ImageField(upload_to='hotel_covers/', blank=True, null=True, help_text="Main cover image")
    
    # Ratings and Reviews
    star_rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Official star rating"
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        help_text="Average customer rating (0.00-5.00)"
    )
    total_reviews = models.PositiveIntegerField(default=0, help_text="Total number of reviews")
    
    # Amenities and Features
    amenities = models.TextField(
        blank=True,
        help_text="List of amenities (comma-separated): WiFi, Pool, Gym, Spa, etc."
    )
    languages_spoken = models.CharField(
        max_length=200,
        blank=True,
        help_text="Languages spoken at reception (comma-separated)"
    )
    
    # Social Media & Branding
    facebook_url = models.URLField(blank=True, help_text="Facebook page URL")
    instagram_url = models.URLField(blank=True, help_text="Instagram profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")
    youtube_url = models.URLField(blank=True, help_text="YouTube channel URL")
    tripadvisor_url = models.URLField(blank=True, help_text="TripAdvisor listing URL")
    booking_com_url = models.URLField(blank=True, help_text="Booking.com listing URL")
    
    # Business Information
    check_in_time = models.TimeField(null=True, blank=True, help_text="Standard check-in time")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Standard check-out time")
    cancellation_policy = models.TextField(blank=True, help_text="Property cancellation policy")
    
    # Microsite Configuration
    custom_domain = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="Custom domain for microsite (e.g., myhotel.com)"
    )
    microsite_enabled = models.BooleanField(
        default=True, 
        help_text="Enable microsite for this property"
    )
    microsite_theme = models.CharField(
        max_length=20,
        choices=[
            ('modern', 'Modern'),
            ('classic', 'Classic'),
            ('luxury', 'Luxury'),
            ('minimal', 'Minimal'),
            ('tropical', 'Tropical'),
        ],
        default='modern',
        help_text="Microsite theme/design"
    )
    microsite_primary_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        help_text="Primary brand color (hex code)"
    )
    microsite_secondary_color = models.CharField(
        max_length=7,
        default='#1E40AF',
        help_text="Secondary brand color (hex code)"
    )
    
    # Status and Meta
    is_active = models.BooleanField(default=True, help_text="Is the property currently active?")
    is_verified = models.BooleanField(default=False, help_text="Has the property been verified?")
    is_featured = models.BooleanField(default=False, help_text="Is this a featured property?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Hotel/Property'
        verbose_name_plural = 'Hotels/Properties'
        indexes = [
            models.Index(fields=['city', 'country']),
            models.Index(fields=['property_type', 'is_active']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_property_type_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('hotel-detail', kwargs={'slug': self.slug})
    
    def get_microsite_url(self, domain='yourdomain.com'):
        """Return microsite URL for this hotel"""
        if self.custom_domain:
            return f"https://{self.custom_domain}/"
        return f"https://{self.slug}.{domain}/"
    
    def get_public_url(self, domain='yourdomain.com'):
        """Return public hotel page URL"""
        return f"https://{domain}/hotel/{self.slug}/"
    
    def get_booking_url(self, domain='yourdomain.com'):
        """Return direct booking URL"""
        if self.custom_domain:
            return f"https://{self.custom_domain}/book/"
        return f"https://{self.slug}.{domain}/book/"
    
    def get_gallery_url(self, domain='yourdomain.com'):
        """Return gallery URL"""
        if self.custom_domain:
            return f"https://{self.custom_domain}/gallery/"
        return f"https://{self.slug}.{domain}/gallery/"
    
    @property
    def location_string(self):
        """Return a formatted location string"""
        parts = [self.city, self.state_province, self.country]
        return ', '.join(filter(None, parts))
    
    @property
    def amenities_list(self):
        """Return amenities as a list"""
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []
    
    @property
    def total_rooms(self):
        """Return total number of rooms"""
        return self.rooms.count()
    
    def get_rating_stars(self):
        """Return rating as full and empty stars"""
        full_stars = int(self.rating)
        half_star = 1 if self.rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        return {
            'full': full_stars,
            'half': half_star,
            'empty': empty_stars
        }

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Administrator'),
        ('hotel_admin', 'Hotel Administrator'),
        ('hotel_staff', 'Hotel Staff'),
        ('customer', 'Customer'),
        ('guest', 'Guest User'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    # Role and Hotel Association
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='customer',
        help_text="User role in the system"
    )
    hotel = models.ForeignKey(
        Hotel, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='staff_members',
        help_text="Associated hotel (for staff members)"
    )
    
    # Extended Profile Information
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in format: '+254712345678'"
    )
    phone = models.CharField(
        validators=[phone_validator], 
        max_length=17, 
        blank=True,
        help_text="Contact phone number"
    )
    address = models.TextField(blank=True, null=True, help_text="Full address")
    city = models.CharField(max_length=100, blank=True, help_text="City")
    country = models.CharField(max_length=100, blank=True, help_text="Country")
    postal_code = models.CharField(max_length=20, blank=True, help_text="Postal/ZIP code")
    
    # Personal Information
    date_of_birth = models.DateField(null=True, blank=True, help_text="Date of birth")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', 
        blank=True, 
        null=True,
        help_text="Profile picture"
    )
    bio = models.TextField(max_length=500, blank=True, help_text="Short bio")
    
    # Preferences
    preferred_language = models.CharField(max_length=10, default='en', help_text="Preferred language code")
    preferred_currency = models.CharField(max_length=3, default='USD', help_text="Preferred currency code")
    receive_notifications = models.BooleanField(default=True, help_text="Receive email notifications")
    receive_marketing = models.BooleanField(default=False, help_text="Receive marketing emails")
    
    # Account Status
    is_verified = models.BooleanField(default=False, help_text="Email verification status")
    phone_verified = models.BooleanField(default=False, help_text="Phone verification status")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['hotel', 'role']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        if self.get_full_name():
            return f"{self.get_full_name()} ({self.username})"
        return self.username
    
    @property
    def full_address(self):
        """Return formatted full address"""
        parts = [self.address, self.city, self.postal_code, self.country]
        return ', '.join(filter(None, parts))
    
    @property
    def is_hotel_staff(self):
        """Check if user is hotel staff"""
        return self.role in ['hotel_admin', 'hotel_staff']
    
    @property
    def is_hotel_admin(self):
        """Check if user is hotel admin"""
        return self.role == 'hotel_admin'
    
    @property
    def is_super_admin(self):
        """Check if user is super admin"""
        return self.role == 'super_admin' or self.is_superuser
    
    def can_manage_hotel(self, hotel):
        """Check if user can manage a specific hotel"""
        if self.is_super_admin:
            return True
        return self.hotel == hotel and self.is_hotel_staff
    
    def get_role_display_badge(self):
        """Return role with appropriate styling class"""
        role_classes = {
            'super_admin': 'badge-danger',
            'hotel_admin': 'badge-warning',
            'hotel_staff': 'badge-info',
            'customer': 'badge-success',
            'guest': 'badge-secondary',
        }
        return {
            'text': self.get_role_display(),
            'class': role_classes.get(self.role, 'badge-secondary')
        }

class UserToken(models.Model):
    TOKEN_TYPES = [
        ('auth', 'Authentication Token'),
        ('reset', 'Password Reset Token'),
        ('verify', 'Email Verification Token'),
        ('phone', 'Phone Verification Token'),
        ('api', 'API Access Token'),
    ]
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=10, choices=TOKEN_TYPES, default='auth')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Token'
        verbose_name_plural = 'User Tokens'
        indexes = [
            models.Index(fields=['token', 'is_active']),
            models.Index(fields=['user', 'token_type']),
        ]
    
    def __str__(self):
        return f'{self.get_token_type_display()} for {self.user.username}'
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.token:
            import secrets
            self.token = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)

# Signal handlers for user management
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile and assign to appropriate group"""
    if created:
        # Assign user to appropriate group based on role
        group_mapping = {
            'super_admin': 'Super Administrators',
            'hotel_admin': 'Hotel Administrators',
            'hotel_staff': 'Hotel Staff',
            'customer': 'Customers',
        }
        
        group_name = group_mapping.get(instance.role)
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            instance.groups.add(group)