#!/usr/bin/env python
"""
Clean up sample image entries and fix production setup
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage

def clean_sample_images():
    """Remove sample image entries that don't have actual files"""
    print("🧹 Cleaning up sample image entries...")
    
    # Find all sample images
    sample_images = RoomImage.objects.filter(image__icontains='sample')
    count = sample_images.count()
    
    if count > 0:
        print(f"Found {count} sample image entries")
        sample_images.delete()
        print(f"✅ Removed {count} sample image entries")
    else:
        print("✅ No sample images found to clean")
    
    # Show current state
    print(f"\n📊 Current state:")
    total_rooms = Room.objects.count()
    total_images = RoomImage.objects.count()
    print(f"   Total rooms: {total_rooms}")
    print(f"   Total images: {total_images}")
    
    # Show rooms without images
    rooms_without_images = Room.objects.filter(images__isnull=True)
    if rooms_without_images.exists():
        print(f"\n📍 Rooms without images:")
        for room in rooms_without_images:
            print(f"   - {room.name} (ID: {room.id})")
        print(f"\n💡 Add images for these rooms in Django admin:")
        print(f"   http://localhost:8000/admin/rentals/roomimage/add/")
    
    # Show rooms with images
    rooms_with_images = Room.objects.filter(images__isnull=False).distinct()
    if rooms_with_images.exists():
        print(f"\n✅ Rooms with images:")
        for room in rooms_with_images:
            images = room.images.all()
            print(f"   - {room.name}: {images.count()} image(s)")
            for img in images:
                print(f"     📸 {img.image}")

if __name__ == '__main__':
    print("🎯 GuestFlow Image Cleanup")
    print("=" * 40)
    
    clean_sample_images()
    
    print("\n" + "=" * 40)
    print("🚀 Cleanup complete!")
    print("\n💡 Next steps:")
    print("   1. Upload real images through Django admin")
    print("   2. Images will be served at: http://localhost:8000/media/room_images/")
    print("   3. API will automatically return full image URLs")
