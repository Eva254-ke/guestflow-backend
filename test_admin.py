#!/usr/bin/env python
"""
Simple admin test script
"""
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test admin site import
    from django.contrib import admin
    from django.contrib.admin.sites import site
    print(f"✅ Admin site loaded: {len(site._registry)} models registered")
    
    # Test user model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    print(f"✅ User model: {User.__name__}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection: OK")
    
    # Test admin URLs
    from django.urls import reverse
    admin_url = reverse('admin:index')
    print(f"✅ Admin URL resolved: {admin_url}")
    
    print("🎉 Basic admin components are working!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
