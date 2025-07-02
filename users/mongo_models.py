from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

class HotelDocument(Document):
    """MongoDB Document for Hotel/Airbnb properties"""
    
    PROPERTY_TYPES = [
        ('hotel', 'Hotel'),
        ('airbnb', 'Airbnb'),
        ('resort', 'Resort'),
        ('hostel', 'Hostel'),
        ('guesthouse', 'Guest House'),
        ('apartment', 'Apartment'),
        ('villa', 'Villa'),
        ('cottage', 'Cottage'),
    ]
    
    # Basic Information
    name = fields.StringField(max_length=200, required=True)
    slug = fields.StringField(max_length=200, unique=True, required=True)
    property_type = fields.StringField(max_length=20, choices=PROPERTY_TYPES, default='hotel')
    
    # Contact Information
    email = fields.EmailField(required=True)
    phone = fields.StringField(max_length=20)
    website = fields.URLField()
    
    # Location
    address = fields.StringField(required=True)
    city = fields.StringField(max_length=100, required=True)
    country = fields.StringField(max_length=100, required=True)
    latitude = fields.DecimalField(precision=6)
    longitude = fields.DecimalField(precision=6)
    
    # Details
    description = fields.StringField()
    amenities = fields.ListField(fields.StringField(max_length=100))
    rules = fields.ListField(fields.StringField(max_length=200))
    
    # Media
    logo_url = fields.URLField()
    images = fields.ListField(fields.URLField())
    
    # Business Details
    rating = fields.DecimalField(min_value=0, max_value=5, precision=2, default=0.00)
    total_reviews = fields.IntField(default=0)
    check_in_time = fields.StringField(max_length=10, default="14:00")
    check_out_time = fields.StringField(max_length=10, default="11:00")
    
    # System Fields
    owner_id = fields.IntField(required=True)  # Reference to Django User
    is_active = fields.BooleanField(default=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'hotels',
        'indexes': ['slug', 'city', 'property_type', 'owner_id']
    }
    
    def __str__(self):
        return f"{self.name} ({self.property_type.title()})"

class RoomDocument(Document):
    """MongoDB Document for Rooms"""
    
    ROOM_TYPES = [
        ('single', 'Single Room'),
        ('double', 'Double Room'),
        ('suite', 'Suite'),
        ('deluxe', 'Deluxe Room'),
        ('family', 'Family Room'),
        ('studio', 'Studio'),
        ('penthouse', 'Penthouse'),
    ]
    
    # Basic Information
    hotel_id = fields.ObjectIdField(required=True)  # Reference to HotelDocument
    name = fields.StringField(max_length=200, required=True)
    room_type = fields.StringField(max_length=20, choices=ROOM_TYPES, default='single')
    room_number = fields.StringField(max_length=10)
    
    # Capacity and Pricing
    capacity = fields.IntField(min_value=1, required=True)
    base_price = fields.DecimalField(min_value=0, precision=2, required=True)
    currency = fields.StringField(max_length=3, default='USD')
    
    # Room Details
    description = fields.StringField()
    size_sqm = fields.IntField(min_value=0)
    bed_type = fields.StringField(max_length=50)
    bed_count = fields.IntField(min_value=1, default=1)
    
    # Amenities and Features
    amenities = fields.ListField(fields.StringField(max_length=100))
    features = fields.ListField(fields.StringField(max_length=100))
    
    # Media
    images = fields.ListField(fields.DictField())  # [{"url": "...", "caption": "...", "is_primary": bool}]
    
    # Availability
    is_available = fields.BooleanField(default=True)
    maintenance_mode = fields.BooleanField(default=False)
    
    # Pricing Rules
    weekend_multiplier = fields.DecimalField(min_value=0, precision=2, default=1.0)
    seasonal_rates = fields.ListField(fields.DictField())  # [{"start_date": "...", "end_date": "...", "multiplier": 1.5}]
    
    # System Fields
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'rooms',
        'indexes': ['hotel_id', 'room_type', 'is_available']
    }
    
    def __str__(self):
        return f"{self.name} - {self.room_type.title()}"

class BookingDocument(Document):
    """MongoDB Document for Bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    # Reference Fields
    hotel_id = fields.ObjectIdField(required=True)
    room_id = fields.ObjectIdField(required=True)
    guest_user_id = fields.IntField()  # Reference to Django User (if registered)
    
    # Booking Details
    booking_reference = fields.StringField(max_length=20, unique=True, required=True)
    check_in_date = fields.DateTimeField(required=True)
    check_out_date = fields.DateTimeField(required=True)
    nights = fields.IntField(min_value=1, required=True)
    guests_count = fields.IntField(min_value=1, required=True)
    
    # Guest Information (for non-registered or override)
    guest_name = fields.StringField(max_length=200)
    guest_email = fields.EmailField()
    guest_phone = fields.StringField(max_length=20)
    guest_address = fields.StringField()
    special_requests = fields.StringField()
    
    # Pricing
    room_rate = fields.DecimalField(precision=2, required=True)
    total_amount = fields.DecimalField(precision=2, required=True)
    taxes = fields.DecimalField(precision=2, default=0.0)
    fees = fields.DecimalField(precision=2, default=0.0)
    currency = fields.StringField(max_length=3, default='USD')
    
    # Status and Dates
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_at = fields.DateTimeField()
    checked_in_at = fields.DateTimeField()
    checked_out_at = fields.DateTimeField()
    cancelled_at = fields.DateTimeField()
    cancellation_reason = fields.StringField()
    
    # Payment Information
    payment_status = fields.StringField(max_length=20, default='pending')
    payment_method = fields.StringField(max_length=50)
    payment_reference = fields.StringField(max_length=100)
    
    # System Fields
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    created_by_user_id = fields.IntField()  # Who created the booking
    
    meta = {
        'collection': 'bookings',
        'indexes': [
            'booking_reference', 
            'hotel_id', 
            'room_id', 
            'check_in_date', 
            'status',
            'guest_email'
        ]
    }
    
    def save(self, *args, **kwargs):
        """Auto-calculate fields before saving"""
        if self.check_in_date and self.check_out_date:
            self.nights = (self.check_out_date.date() - self.check_in_date.date()).days
        
        self.updated_at = datetime.utcnow()
        
        # Generate booking reference if not exists
        if not self.booking_reference:
            import uuid
            self.booking_reference = str(uuid.uuid4())[:8].upper()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Booking {self.booking_reference} - {self.guest_name or 'Unknown Guest'}"

class ReviewDocument(Document):
    """MongoDB Document for Reviews"""
    
    # Reference Fields
    hotel_id = fields.ObjectIdField(required=True)
    booking_id = fields.ObjectIdField()
    guest_user_id = fields.IntField()  # Reference to Django User
    
    # Review Content
    rating = fields.IntField(min_value=1, max_value=5, required=True)
    title = fields.StringField(max_length=200)
    comment = fields.StringField()
    
    # Detailed Ratings
    cleanliness_rating = fields.IntField(min_value=1, max_value=5)
    service_rating = fields.IntField(min_value=1, max_value=5)
    location_rating = fields.IntField(min_value=1, max_value=5)
    value_rating = fields.IntField(min_value=1, max_value=5)
    
    # Guest Information
    guest_name = fields.StringField(max_length=200)
    guest_email = fields.EmailField()
    
    # Status
    is_approved = fields.BooleanField(default=False)
    is_featured = fields.BooleanField(default=False)
    
    # Response from Hotel
    hotel_response = fields.StringField()
    responded_at = fields.DateTimeField()
    
    # System Fields
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'reviews',
        'indexes': ['hotel_id', 'rating', 'is_approved', 'created_at']
    }
    
    def __str__(self):
        return f"Review by {self.guest_name} - {self.rating}/5"
