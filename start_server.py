#!/usr/bin/env python
"""
Production-ready Django server startup script for GuestFlow
"""

import os
import sys
import subprocess
from pathlib import Path

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error in makemigrations: {result.stderr}")
    else:
        print("✅ Migrations created successfully")
    
    result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error in migrate: {result.stderr}")
        return False
    else:
        print("✅ Migrations applied successfully")
        return True

def setup_media_files():
    """Setup media files and sample images"""
    print("🔄 Setting up media files...")
    result = subprocess.run([sys.executable, 'create_sample_images.py'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error setting up media files: {result.stderr}")
    else:
        print("✅ Media files setup complete")

def setup_test_data():
    """Setup test data"""
    print("🔄 Setting up test data...")
    result = subprocess.run([sys.executable, 'test_data_setup.py'], 
                          capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error setting up test data: {result.stderr}")
    else:
        print("✅ Test data setup complete")

def start_server():
    """Start Django development server"""
    print("🚀 Starting Django server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📍 API endpoints will be at: http://localhost:8000/api/")
    print("🔗 Admin panel: http://localhost:8000/admin/")
    print("\n📋 Available API endpoints:")
    print("  - GET /api/rentals/{slug}/rooms/ - Get available rooms")
    print("  - GET /api/daily-prices/ - Get daily room prices")
    print("\n💡 Test with rental slug: 'luxury-hotel'")
    print("\n⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'manage.py', 'runserver', '8000'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main function to setup and run Django server"""
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ manage.py not found. Please run this script from the Django project root.")
        sys.exit(1)
    
    print("🎯 GuestFlow Django Server Setup")
    print("=" * 40)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migration failed. Please check your database configuration.")
        sys.exit(1)
    
    # Setup test data
    setup_test_data()
    
    # Setup media files
    setup_media_files()
    
    print("\n" + "=" * 40)
    
    # Start server
    start_server()

if __name__ == '__main__':
    main()
