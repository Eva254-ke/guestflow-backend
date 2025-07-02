#!/usr/bin/env python
"""
Django diagnostics script to check common issues that might cause 500 errors
"""
import os
import django
from django.conf import settings

# Load .env file if it exists
try:
    from decouple import config
    # This will load the .env file
    SECRET_KEY = config('SECRET_KEY', default='NOT SET')
    DEBUG = config('DEBUG', default=False, cast=bool)
    print("✅ .env file loaded successfully")
except Exception as e:
    print(f"⚠️  Could not load .env file: {e}")

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guestflow_project.settings')
django.setup()

def check_database():
    """Check if database connection works"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def check_mongodb():
    """Check MongoDB connection"""
    try:
        import mongoengine
        # Test the connection
        from mongoengine.connection import get_connection
        db = get_connection()
        db.admin.command('ping')
        print("✅ MongoDB connection: OK")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection: FAILED - {e}")
        return False

def check_user_model():
    """Check if custom user model works"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        # Try to get a user (this will test model loading)
        users = User.objects.all()[:1]
        print(f"✅ Custom User model: OK - Found {User.objects.count()} users")
        return True
    except Exception as e:
        print(f"❌ Custom User model: FAILED - {e}")
        return False

def check_migrations():
    """Check if all migrations are applied"""
    try:
        from django.core.management import execute_from_command_line
        from io import StringIO
        import sys
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        
        try:
            execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
            output = mystdout.getvalue()
            sys.stdout = old_stdout
            
            if '[X]' in output and '[ ]' not in output:
                print("✅ Migrations: All applied")
                return True
            else:
                print("❌ Migrations: Some unapplied migrations found")
                print(output)
                return False
        except:
            sys.stdout = old_stdout
            print("⚠️  Could not check migrations status")
            return False
    except Exception as e:
        print(f"❌ Migrations check: FAILED - {e}")
        return False

def check_admin_site():
    """Check if admin site can be imported and configured"""
    try:
        from django.contrib import admin
        from django.contrib.admin.sites import site
        print(f"✅ Admin site: OK - {len(site._registry)} models registered")
        return True
    except Exception as e:
        print(f"❌ Admin site: FAILED - {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n📋 Environment Variables:")
    from decouple import config
    env_vars = [
        'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS',
        'MONGODB_URI', 'MONGODB_NAME'
    ]
    
    all_good = True
    for var in env_vars:
        try:
            if var == 'DEBUG':
                value = config(var, default='NOT SET', cast=bool)
            else:
                value = config(var, default='NOT SET')
            
            if var == 'SECRET_KEY' and value != 'NOT SET':
                value = value[:10] + '...' if len(str(value)) > 10 else str(value)
            print(f"  {var}: {value}")
            if value == 'NOT SET':
                all_good = False
        except Exception as e:
            print(f"  {var}: ERROR - {e}")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🔍 Django Diagnostics Report")
    print("=" * 50)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Database Connection", check_database),
        ("MongoDB Connection", check_mongodb),
        ("Custom User Model", check_user_model),
        ("Migrations Status", check_migrations),
        ("Admin Site", check_admin_site),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔎 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}: EXCEPTION - {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    
    if passed < total:
        print("❌ Issues found. Check the detailed output above.")
    else:
        print("🎉 All checks passed!")
