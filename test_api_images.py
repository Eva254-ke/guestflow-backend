#!/usr/bin/env python
"""
Test API response for room images
"""

import os
import django
import requests

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

from rentals.models import Room, RoomImage

def check_database():
    """Check what's in the database"""
    print("🔍 CHECKING DATABASE")
    print("=" * 50)
    
    from rentals.models import Rental
    
    # Check rentals first
    rentals = Rental.objects.all()
    print(f"Total rentals: {rentals.count()}")
    for rental in rentals:
        print(f"📍 Rental: {rental.name} (slug: {rental.slug})")
    
    rooms = Room.objects.all()
    print(f"\nTotal rooms: {rooms.count()}")
    
    for room in rooms:
        print(f"\n📍 Room: {room.name} (ID: {room.id})")
        print(f"   Rental: {room.rental.name} (slug: {room.rental.slug})")
        images = room.images.all()
        print(f"   Images count: {images.count()}")
        
        for img in images:
            print(f"   📸 Image: {img.image.name}")
            print(f"      URL: {img.image.url}")
            if img.image:
                file_path = img.image.path
                exists = os.path.exists(file_path)
                print(f"      File exists: {exists}")
                print(f"      Full path: {file_path}")
    
    # Check all room images
    all_images = RoomImage.objects.all()
    print(f"\nTotal room images in database: {all_images.count()}")
    for img in all_images:
        print(f"📸 Image ID: {img.id}, Room: {img.room.name}, File: {img.image.name}")

def test_api_response():
    """Test the actual API response"""
    print("\n🌐 TESTING API RESPONSE")
    print("=" * 50)
    
    # Test with the known rental slug
    rental_slug = "cozy-nairobi-airbnb"
    api_url = f"http://localhost:8000/api/rentals/{rental_slug}/rooms/"
    print(f"🔗 Testing URL: {api_url}")
    
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Response Status: {response.status_code}")
            print(f"📊 Number of rooms returned: {len(data)}")
            
            for room in data:
                print(f"\n📍 Room: {room.get('name')} (ID: {room.get('id')})")
                images = room.get('images', [])
                print(f"   Images count: {len(images)}")
                
                if len(images) == 0:
                    print("   ❌ No images found in API response")
                
                for img in images:
                    print(f"   📸 Image URL: {img.get('image')}")
                    
                    # Test if image URL is accessible
                    if img.get('image'):
                        try:
                            img_response = requests.head(img.get('image'))
                            print(f"      Image accessible: {img_response.status_code == 200}")
                        except Exception as e:
                            print(f"      Image test failed: {e}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Also test all available rentals
    print(f"\n🔍 Testing all available rentals:")
    from rentals.models import Rental
    rentals = Rental.objects.all()
    
    for rental in rentals:
        test_url = f"http://localhost:8000/api/rentals/{rental.slug}/rooms/"
        print(f"   📍 {rental.name}: {test_url}")

def main():
    print("🎯 TESTING ROOM IMAGES")
    print("=" * 50)
    
    # Check database first
    check_database()
    
    # Then test API
    test_api_response()
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    print("\n💡 If images are not showing:")
    print("   1. Make sure Django server is running: python manage.py runserver")
    print("   2. Check the image URLs in browser")
    print("   3. Verify image files exist in mediafiles/room_images/")

if __name__ == '__main__':
    main()
