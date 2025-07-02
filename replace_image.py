#!/usr/bin/env python
"""
Replace .txt placeholder with real image
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage
from django.conf import settings

def replace_placeholder_image():
    """Replace the .txt placeholder with a real image"""
    print("🎯 REPLACING PLACEHOLDER IMAGE")
    print("=" * 50)
    
    # Get the room
    room = Room.objects.get(id=1)
    print(f"📍 Room: {room.name} (ID: {room.id})")
    
    # Check current images
    current_images = room.images.all()
    print(f"📊 Current images: {current_images.count()}")
    
    # Find and remove .txt placeholder
    txt_images = current_images.filter(image__icontains='.txt')
    if txt_images.exists():
        print(f"\n🗑️ Removing {txt_images.count()} .txt placeholder(s):")
        for img in txt_images:
            print(f"   📸 Removing: {img.image.name}")
            # Delete the file if it exists
            try:
                if os.path.exists(img.image.path):
                    os.remove(img.image.path)
                    print(f"   ✅ Deleted file: {img.image.path}")
            except Exception as e:
                print(f"   ⚠️ Could not delete file: {e}")
            # Delete the database entry
            img.delete()
            print(f"   ✅ Removed from database")
    
    # List available real image files
    room_images_dir = os.path.join(settings.MEDIA_ROOT, 'room_images')
    
    try:
        files = [f for f in os.listdir(room_images_dir) 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')) 
                and not f.endswith('.txt')]
        
        if files:
            print(f"\n📂 Available real image files:")
            for i, file in enumerate(files, 1):
                file_path = os.path.join(room_images_dir, file)
                file_size = os.path.getsize(file_path)
                print(f"   {i}. {file} ({file_size:,} bytes)")
            
            if len(files) == 1:
                # Auto-select if only one image
                selected_file = files[0]
                print(f"\n✅ Auto-selecting: {selected_file}")
            else:
                try:
                    choice = int(input(f"\n❓ Select image (1-{len(files)}): "))
                    if 1 <= choice <= len(files):
                        selected_file = files[choice - 1]
                    else:
                        print("❌ Invalid selection")
                        return
                except ValueError:
                    print("❌ Invalid input")
                    return
            
            # Create new RoomImage entry
            image_path = f'room_images/{selected_file}'
            room_image = RoomImage.objects.create(
                room=room,
                image=image_path
            )
            
            print(f"\n✅ Added real image: {selected_file}")
            print(f"   📸 Image ID: {room_image.id}")
            print(f"   🔗 Image URL: {room_image.image.url}")
            
            # Build full URL for testing
            full_url = f"http://localhost:8000{room_image.image.url}"
            print(f"   🌐 Full URL: {full_url}")
            
        else:
            print(f"\n❌ No real image files found in {room_images_dir}")
            print("   📥 Please copy your image files (.jpg, .png, etc.) to this directory")
            
    except FileNotFoundError:
        print(f"❌ Cannot access directory: {room_images_dir}")

def verify_final_state():
    """Verify the final state"""
    print("\n🔍 FINAL VERIFICATION")
    print("=" * 30)
    
    room = Room.objects.get(id=1)
    images = room.images.all()
    
    print(f"📊 Total images for {room.name}: {images.count()}")
    
    for img in images:
        print(f"\n📸 Image ID: {img.id}")
        print(f"   📁 File: {img.image.name}")
        print(f"   🔗 URL: {img.image.url}")
        print(f"   🌐 Full URL: http://localhost:8000{img.image.url}")
        
        # Check file
        try:
            file_exists = os.path.exists(img.image.path)
            print(f"   ✅ File exists: {file_exists}")
            if file_exists:
                file_size = os.path.getsize(img.image.path)
                print(f"   📊 File size: {file_size:,} bytes")
        except Exception as e:
            print(f"   ❌ File check error: {e}")

if __name__ == '__main__':
    print("🏨 IMAGE REPLACEMENT TOOL")
    print("=" * 50)
    
    replace_placeholder_image()
    verify_final_state()
    
    print("\n" + "=" * 50)
    print("✅ Done!")
    print("\n🔄 Test the API again with:")
    print("   python test_api_images.py")
    print("\n🌐 Or test in browser:")
    print("   http://localhost:8000/api/rentals/cozy-nairobi-airbnb/rooms/")
