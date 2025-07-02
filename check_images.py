#!/usr/bin/env python
"""
Quick check script to verify room images in database
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage

def check_rooms_and_images():
    """Check all rooms and their images"""
    print("🔍 Current Room and Image Status:")
    print("=" * 50)
    
    rooms = Room.objects.all()
    print(f"Total Rooms: {rooms.count()}")
    
    for room in rooms:
        print(f"\n📍 Room: {room.name} (ID: {room.id})")
        print(f"   Capacity: {room.capacity}")
        print(f"   Base Price: ${room.base_price}")
        
        images = room.images.all()
        print(f"   Images: {images.count()}")
        
        for img in images:
            print(f"     └─ {img.id}: {img.image}")
    
    # Total statistics
    total_images = RoomImage.objects.count()
    rooms_with_images = Room.objects.filter(images__isnull=False).distinct().count()
    
    print(f"\n📊 Summary:")
    print(f"   Total Rooms: {rooms.count()}")
    print(f"   Rooms with Images: {rooms_with_images}")
    print(f"   Total Images: {total_images}")
    
    if rooms_with_images < rooms.count():
        print(f"\n⚠️  {rooms.count() - rooms_with_images} rooms missing images!")
        print("   Run: python add_room_images.py")
    else:
        print(f"\n✅ All rooms have images!")

if __name__ == '__main__':
    check_rooms_and_images()
