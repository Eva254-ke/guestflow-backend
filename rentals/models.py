from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import Hotel, CustomUser
import uuid

class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('twin', 'Twin Room'),
        ('king', 'King Room'),
        ('queen', 'Queen Room'),
        ('presidential', 'Presidential Suite'),
        ('penthouse', 'Penthouse'),
        ('studio', 'Studio Apartment'),
        ('one_bedroom', '1 Bedroom Apartment'),
        ('two_bedroom', '2 Bedroom Apartment'),
        ('three_bedroom', '3 Bedroom Apartment'),
        ('villa', 'Private Villa'),
        ('cottage', 'Cottage'),
        ('cabin', 'Cabin'),
        ('loft', 'Loft'),
        ('dormitory', 'Dormitory Bed'),
    ]
    
    BED_TYPES = [
        ('single', 'Single Bed'),
        ('double', 'Double Bed'),
        ('queen', 'Queen Bed'),
        ('king', 'King Bed'),
        ('twin', 'Twin Beds'),
        ('bunk', 'Bunk Bed'),
        ('sofa', 'Sofa Bed'),
    ]
    
    BATHROOM_TYPES = [
        ('private', 'Private Bathroom'),
        ('ensuite', 'En-suite Bathroom'),
        ('shared', 'Shared Bathroom'),
        ('half', 'Half Bathroom'),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=200, help_text="Room name/number")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, help_text="Type of room")
    
    # Room Details
    description = models.TextField(help_text="Detailed room description")
    short_description = models.CharField(max_length=300, blank=True, help_text="Brief description")
    
    # Capacity
    max_occupancy = models.PositiveIntegerField(help_text="Maximum number of guests")
    adults = models.PositiveIntegerField(default=2, help_text="Number of adults")
    children = models.PositiveIntegerField(default=0, help_text="Number of children")
    infants = models.PositiveIntegerField(default=0, help_text="Number of infants")
    
    # Room Specifications
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Room size in square meters")
    bed_type = models.CharField(max_length=20, choices=BED_TYPES, help_text="Type of bed")
    number_of_beds = models.PositiveIntegerField(default=1, help_text="Number of beds")
    bathroom_type = models.CharField(max_length=20, choices=BATHROOM_TYPES, help_text="Bathroom type")
    
    # Amenities
    amenities = models.TextField(blank=True, help_text="Room amenities (comma-separated)")
    has_wifi = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_tv = models.BooleanField(default=True)
    has_balcony = models.BooleanField(default=False)
    has_kitchen = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price per night")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code")
    
    # Availability
    is_available = models.BooleanField(default=True, help_text="Is room currently available?")
    min_stay = models.PositiveIntegerField(default=1, help_text="Minimum nights required")
    max_stay = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum nights allowed")
    
    # Check-in/out times
    check_in_time = models.TimeField(null=True, blank=True, help_text="Room-specific check-in time")
    check_out_time = models.TimeField(null=True, blank=True, help_text="Room-specific check-out time")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['hotel', 'name']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        indexes = [
            models.Index(fields=['hotel', 'is_available']),
            models.Index(fields=['room_type', 'is_active']),
            models.Index(fields=['base_price']),
        ]
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name} ({self.get_room_type_display()})"
    
    @property
    def amenities_list(self):
        """Return amenities as a list"""
        if self.amenities:
            return [amenity.strip() for amenity in self.amenities.split(',')]
        return []
    
    @property
    def primary_image(self):
        """Get the primary image for this room"""
        return self.images.filter(is_primary=True).first()
    
    @property
    def all_images(self):
        """Get all images for this room"""
        return self.images.all().order_by('-is_primary', 'order')

class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/', help_text="Room image")
    caption = models.CharField(max_length=200, blank=True, help_text="Image caption")
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alt text for accessibility")
    is_primary = models.BooleanField(default=False, help_text="Is this the main image?")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'order']
        verbose_name = 'Room Image'
        verbose_name_plural = 'Room Images'
        indexes = [
            models.Index(fields=['room', 'is_primary']),
        ]
    
    def __str__(self):
        return f"{self.room.name} - Image {self.order}"
    
    def save(self, *args, **kwargs):
        # Ensure only one primary image per room
        if self.is_primary:
            RoomImage.objects.filter(room=self.room).update(is_primary=False)
        super().save(*args, **kwargs)

class RoomPricing(models.Model):
    PRICING_TYPES = [
        ('base', 'Base Price'),
        ('weekend', 'Weekend Price'),
        ('holiday', 'Holiday Price'),
        ('seasonal', 'Seasonal Price'),
        ('special', 'Special Event Price'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='pricing')
    pricing_type = models.CharField(max_length=20, choices=PRICING_TYPES, default='base')
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night")
    currency = models.CharField(max_length=3, default='USD')
    
    # Date range for pricing
    start_date = models.DateField(null=True, blank=True, help_text="Start date for this pricing")
    end_date = models.DateField(null=True, blank=True, help_text="End date for this pricing")
    
    # Day-specific pricing
    monday = models.BooleanField(default=True)
    tuesday = models.BooleanField(default=True)
    wednesday = models.BooleanField(default=True)
    thursday = models.BooleanField(default=True)
    friday = models.BooleanField(default=True)
    saturday = models.BooleanField(default=True)
    sunday = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Room Pricing'
        verbose_name_plural = 'Room Pricing'
    
    def __str__(self):
        return f"{self.room.name} - {self.get_pricing_type_display()}: ${self.price}"

class RoomAvailability(models.Model):
    AVAILABILITY_STATUS = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField(help_text="Date")
    status = models.CharField(max_length=20, choices=AVAILABILITY_STATUS, default='available')
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Override price for this date")
    notes = models.TextField(blank=True, help_text="Notes about availability")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['room', 'date']
        ordering = ['date']
        verbose_name = 'Room Availability'
        verbose_name_plural = 'Room Availability'
        indexes = [
            models.Index(fields=['room', 'date']),
            models.Index(fields=['status', 'date']),
        ]
    
    def __str__(self):
        return f"{self.room.name} - {self.date} ({self.get_status_display()})"

# Keep existing Rental model for backward compatibility
class Rental(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rentals')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} - ${self.price_per_night}/night"

class RoomFee(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='fees')
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_percentage = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.room.name} - {self.name}"

class RoomTax(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='taxes')
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_inclusive = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.room.name} - {self.name}"