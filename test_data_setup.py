#!/usr/bin/env python
"""
Test data setup script for GuestFlow
Run this script to populate your database with sample data for testing
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from rentals.models import Rental, Room, RoomImage
from bookings.models import DailyRoomPrice, ExchangeRate
from datetime import date, timedelta
from decimal import Decimal
from django.core.files.base import ContentFile
import os

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Create a test user
    user, created = User.objects.get_or_create(
        username='testowner',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'Owner'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✓ Created test user")
    
    # Create a test rental
    rental, created = Rental.objects.get_or_create(
        slug='luxury-hotel',
        defaults={
            'owner': user,
            'name': 'Luxury Downtown Hotel',
            'description': 'A modern luxury hotel in the heart of the city with stunning views and premium amenities.',
            'latitude': Decimal('40.7589'),
            'longitude': Decimal('-73.9851')
        }
    )
    if created:
        print("✓ Created test rental")
    
    # Create test rooms
    rooms_data = [
        {
            'name': 'Classic Queen',
            'base_price': Decimal('186.00'),
            'capacity': 2,
            'description': 'Classic Queen Rooms feature one Queen sized bed, and have SoHo views from the floor to ceiling windows. Located between the 3rd — 24th floor.'
        },
        {
            'name': 'Deluxe King',
            'base_price': Decimal('225.00'),
            'capacity': 2,
            'description': 'Spacious deluxe rooms with king-sized bed, marble bathroom, and city skyline views. Premium amenities included.'
        },
        {
            'name': 'Executive Suite',
            'base_price': Decimal('350.00'),
            'capacity': 4,
            'description': 'Luxurious suite with separate living area, king bedroom, premium furnishings, and panoramic city views.'
        }
    ]
    
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            rental=rental,
            name=room_data['name'],
            defaults=room_data
        )
        if created:
            print(f"✓ Created room: {room.name}")
        
        # Create sample daily prices for the next 30 days
        today = date.today()
        for i in range(30):
            price_date = today + timedelta(days=i)
            # Vary prices slightly (weekend premium)
            base_price = room.base_price
            if price_date.weekday() >= 5:  # Weekend
                base_price = base_price * Decimal('1.2')
            
            DailyRoomPrice.objects.get_or_create(
                room=room,
                date=price_date,
                defaults={'price': base_price}
            )
    
    # Create exchange rate (USD as base)
    ExchangeRate.objects.get_or_create(
        currency='USD',
        defaults={'rate': Decimal('1.00')}
    )
    
    print("✅ Test data setup complete!")
    print("\nYou can now test with:")
    print("- Rental slug: 'luxury-hotel'")
    print("- Rooms: Classic Queen, Deluxe King, Executive Suite")
    print("- Dates: Any date from today to next 30 days")

if __name__ == '__main__':
    create_test_data()
