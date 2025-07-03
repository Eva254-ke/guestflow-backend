@echo off
echo Pushing diagnostic script updates to GitHub...
git add diagnose.py
git commit -m "Update diagnostic script to properly load environment variables"
git push origin main
echo Done!
pause
