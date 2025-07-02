#!/usr/bin/env python
"""
Create sample room images for testing
"""

import os
import django
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from django.conf import settings
from rentals.models import Room, RoomImage

def create_media_structure():
    """Create media directory structure"""
    media_root = Path(settings.MEDIA_ROOT)
    room_images_dir = media_root / 'room_images'
    
    # Create directories
    room_images_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created media directory: {room_images_dir}")
    
    # Create sample gradient images (placeholder)
    sample_images = [
        'classic_queen.jpg',
        'deluxe_king.jpg', 
        'executive_suite.jpg'
    ]
    
    for image_name in sample_images:
        image_path = room_images_dir / image_name
        if not image_path.exists():
            # Create a simple placeholder file
            with open(image_path, 'w') as f:
                f.write("# Placeholder image file\n")
            print(f"  ✓ Created placeholder: {image_name}")
    
    print("\n💡 Note: These are placeholder files.")
    print("   In production, upload actual room images through Django admin.")
    print(f"   Media URL: {settings.MEDIA_URL}")
    print(f"   Media Root: {settings.MEDIA_ROOT}")

def link_images_to_rooms():
    """Link sample images to rooms"""
    rooms = Room.objects.all()
    image_names = ['classic_queen.jpg', 'deluxe_king.jpg', 'executive_suite.jpg']
    
    for i, room in enumerate(rooms):
        if i < len(image_names):
            image_name = image_names[i]
            room_image, created = RoomImage.objects.get_or_create(
                room=room,
                defaults={'image': f'room_images/{image_name}'}
            )
            if created:
                print(f"✓ Linked {image_name} to {room.name}")

if __name__ == '__main__':
    print("🎯 Creating Sample Room Images")
    print("=" * 40)
    
    create_media_structure()
    link_images_to_rooms()
    
    print("\n✅ Sample images setup complete!")
    print("\n🔧 To add real images:")
    print("   1. Upload images to backend/mediafiles/room_images/")
    print("   2. Update RoomImage objects in Django admin")
    print("   3. Or use the Django admin interface to upload images")
