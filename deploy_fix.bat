@echo off
cd "c:\Users\Admin\OneDrive\Desktop\guest\GuestFlow\backend"
echo Current directory: %CD%
git add .
git commit -m "Fix MongoDB connection handling and update STORAGES for Django 5.x"
git push origin main
echo Git operations completed
pause
