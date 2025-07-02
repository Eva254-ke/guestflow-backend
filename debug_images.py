#!/usr/bin/env python
"""
Debug script to check room images in database
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage
from django.conf import settings

def check_room_images():
    print("🔍 CHECKING ROOM IMAGES IN DATABASE")
    print("=" * 50)
    
    rooms = Room.objects.all()
    print(f"Total rooms: {rooms.count()}")
    
    for room in rooms:
        print(f"\n📍 Room: {room.name} (ID: {room.id})")
        images = room.images.all()
        print(f"   Images count: {images.count()}")
        
        for img in images:
            print(f"   📸 Image file: {img.image}")
            if img.image:
                print(f"      URL: {img.image.url}")
                # Check if file exists
                file_path = os.path.join(settings.MEDIA_ROOT, str(img.image))
                exists = os.path.exists(file_path)
                print(f"      File exists: {exists}")
                if not exists:
                    print(f"      Expected path: {file_path}")
            else:
                print(f"      ❌ No image file")
        
        if images.count() == 0:
            print("   ❌ No images found for this room")
    
    print(f"\n📁 Media settings:")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    
    # Check if media directory exists
    media_dir = settings.MEDIA_ROOT
    if os.path.exists(media_dir):
        print(f"   ✅ Media directory exists: {media_dir}")
        room_images_dir = os.path.join(media_dir, 'room_images')
        if os.path.exists(room_images_dir):
            print(f"   ✅ Room images directory exists")
            files = os.listdir(room_images_dir)
            print(f"   📂 Files in room_images: {files}")
        else:
            print(f"   ❌ Room images directory doesn't exist: {room_images_dir}")
    else:
        print(f"   ❌ Media directory doesn't exist: {media_dir}")

if __name__ == '__main__':
    check_room_images()
