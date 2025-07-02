@echo off
echo ================================
echo GuestFlow Backend Deployment Fix
echo ================================

cd /d "c:\Users\Admin\OneDrive\Desktop\guest\GuestFlow\backend"
echo Current directory: %CD%

echo.
echo 1. Checking git status...
git status

echo.
echo 2. Adding all changes...
git add .

echo.
echo 3. Committing changes...
git commit -m "Fix MongoDB connection handling, update STORAGES for Django 5.x, and improve admin panel stability"

echo.
echo 4. Pushing to GitHub...
git push origin main

echo.
echo 5. Deployment pushed to Railway. 
echo    Check https://web-production-e29be.up.railway.app/admin/ 
echo    to see if the 500 error is resolved.

echo.
echo 6. If the issue persists, the diagnostics scripts can help:
echo    - diagnose.py: Run comprehensive diagnostics
echo    - test_admin.py: Test admin panel specifically

echo.
echo Deployment complete! 
pause
