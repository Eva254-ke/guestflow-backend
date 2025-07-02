#!/usr/bin/env python
"""
Add room image through Django script
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage
from django.core.files.base import ContentFile

def add_room_image():
    """Add an image to the room"""
    print("🎯 ADDING ROOM IMAGE")
    print("=" * 50)
    
    # Get the room
    try:
        room = Room.objects.get(id=1)
        print(f"✅ Found room: {room.name} (ID: {room.id})")
    except Room.DoesNotExist:
        print("❌ Room with ID 1 not found!")
        return
    
    # Check current images
    current_images = room.images.count()
    print(f"📊 Current images for this room: {current_images}")
    
    if current_images > 0:
        print("🔍 Existing images:")
        for img in room.images.all():
            print(f"   📸 {img.image.name}")
        
        choice = input("\n❓ Do you want to add another image? (y/n): ")
        if choice.lower() != 'y':
            return
    
    # List available image files in mediafiles/room_images/
    from django.conf import settings
    room_images_dir = os.path.join(settings.MEDIA_ROOT, 'room_images')
    
    if not os.path.exists(room_images_dir):
        print(f"❌ Room images directory doesn't exist: {room_images_dir}")
        print("   Creating directory...")
        os.makedirs(room_images_dir, exist_ok=True)
    
    # List files in room_images directory
    try:
        files = [f for f in os.listdir(room_images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        if files:
            print(f"\n📂 Available image files in {room_images_dir}:")
            for i, file in enumerate(files, 1):
                print(f"   {i}. {file}")
            
            try:
                choice = int(input(f"\n❓ Select image (1-{len(files)}) or 0 to create sample: "))
                if 1 <= choice <= len(files):
                    selected_file = files[choice - 1]
                    image_path = f'room_images/{selected_file}'
                    
                    # Create RoomImage entry
                    room_image = RoomImage.objects.create(
                        room=room,
                        image=image_path
                    )
                    print(f"✅ Added image: {selected_file}")
                    print(f"   Image ID: {room_image.id}")
                    print(f"   Image URL: {room_image.image.url}")
                    
                elif choice == 0:
                    create_sample_image(room)
                else:
                    print("❌ Invalid selection")
                    
            except ValueError:
                print("❌ Invalid input")
        else:
            print(f"\n📂 No image files found in {room_images_dir}")
            create_sample_image(room)
            
    except FileNotFoundError:
        print(f"❌ Cannot access directory: {room_images_dir}")
        create_sample_image(room)

def create_sample_image(room):
    """Create a sample image file and database entry"""
    print("\n🎨 Creating sample image...")
    
    from django.conf import settings
    import datetime
    
    # Create a simple text file as placeholder
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"room_{room.id}_{timestamp}.txt"
    file_path = os.path.join(settings.MEDIA_ROOT, 'room_images', filename)
    
    # Create the file
    with open(file_path, 'w') as f:
        f.write(f"Sample image placeholder for {room.name}\n")
        f.write(f"Created: {datetime.datetime.now()}\n")
        f.write("Replace this with a real image file (.jpg, .png, etc.)\n")
    
    # Create database entry
    image_path = f'room_images/{filename}'
    room_image = RoomImage.objects.create(
        room=room,
        image=image_path
    )
    
    print(f"✅ Created sample image: {filename}")
    print(f"   Image ID: {room_image.id}")
    print(f"   Image URL: {room_image.image.url}")
    print(f"   File path: {file_path}")
    
    print("\n💡 To use a real image:")
    print("   1. Copy your image file to: mediafiles/room_images/")
    print("   2. Run this script again to link it to the room")

def verify_images():
    """Verify images after adding"""
    print("\n🔍 VERIFICATION")
    print("=" * 30)
    
    room = Room.objects.get(id=1)
    images = room.images.all()
    
    print(f"📊 Total images for {room.name}: {images.count()}")
    
    for img in images:
        print(f"\n📸 Image ID: {img.id}")
        print(f"   File: {img.image.name}")
        print(f"   URL: {img.image.url}")
        
        # Check if file exists
        try:
            file_exists = os.path.exists(img.image.path)
            print(f"   File exists: {file_exists}")
            if file_exists:
                file_size = os.path.getsize(img.image.path)
                print(f"   File size: {file_size} bytes")
        except Exception as e:
            print(f"   File check error: {e}")

if __name__ == '__main__':
    print("🏨 ROOM IMAGE MANAGER")
    print("=" * 50)
    
    add_room_image()
    verify_images()
    
    print("\n" + "=" * 50)
    print("✅ Done!")
    print("\n🔄 Test the API again with:")
    print("   python test_api_images.py")
