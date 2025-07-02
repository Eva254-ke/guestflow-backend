#!/usr/bin/env python
"""
Production-ready media setup for GuestFlow
Creates proper directory structure for uploaded images
"""
import os
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from django.conf import settings

def setup_media_directories():
    """Create media directory structure"""
    print("🔧 Setting up media directories...")
    
    # Get media root from settings
    media_root = Path(settings.MEDIA_ROOT)
    room_images_dir = media_root / 'room_images'
    
    # Create directories
    media_root.mkdir(exist_ok=True)
    room_images_dir.mkdir(exist_ok=True)
    
    print(f"✅ Created media root: {media_root}")
    print(f"✅ Created room images directory: {room_images_dir}")
    
    # Set permissions (for Unix systems)
    try:
        os.chmod(media_root, 0o755)
        os.chmod(room_images_dir, 0o755)
        print("✅ Set directory permissions")
    except:
        print("ℹ️  Could not set permissions (Windows system)")
    
    print(f"\n📁 Media configuration:")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"   Full path: {media_root.absolute()}")

def check_existing_images():
    """Check existing uploaded images"""
    print("\n🔍 Checking existing images...")
    
    from rentals.models import Room, RoomImage
    
    total_rooms = Room.objects.count()
    total_images = RoomImage.objects.count()
    
    print(f"📊 Database status:")
    print(f"   Total rooms: {total_rooms}")
    print(f"   Total images: {total_images}")
    
    if total_images > 0:
        print(f"\n📸 Images found:")
        for img in RoomImage.objects.all():
            print(f"   - Room: {img.room.name}")
            print(f"     File: {img.image}")
            if img.image:
                full_path = Path(settings.MEDIA_ROOT) / str(img.image)
                exists = full_path.exists()
                print(f"     Exists: {'✅' if exists else '❌'}")
                if exists:
                    size = full_path.stat().st_size
                    print(f"     Size: {size} bytes")
    else:
        print("   No images found. Please upload images through Django admin.")

if __name__ == '__main__':
    print("🎯 GuestFlow Media Setup")
    print("=" * 40)
    
    setup_media_directories()
    check_existing_images()
    
    print("\n" + "=" * 40)
    print("🚀 Setup complete!")
    print("\n💡 Next steps:")
    print("   1. Upload room images through Django admin")
    print("   2. Images will be available at: http://localhost:8000/media/room_images/")
    print("   3. API will return full image URLs automatically")
