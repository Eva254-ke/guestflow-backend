@echo off
echo Setting Railway environment variables...

railway variables set SECRET_KEY="django-production-secret-key-railway-2025"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="*.railway.app"
railway variables set MONGODB_URI="mongodb+srv://nexareality66:DoUK5lQoWPWc4XNw@cluster0.n07rudg.mongodb.net/?retryWrites=true&w=majority"
railway variables set MONGODB_NAME="guestflow"
railway variables set MONGODB_USERNAME="nexareality66"
railway variables set MONGODB_PASSWORD="DoUK5lQoWPWc4XNw"
railway variables set MONGODB_AUTH_SOURCE="admin"
railway variables set CORS_ALLOWED_ORIGINS="https://*.railway.app"
railway variables set CSRF_TRUSTED_ORIGINS="https://*.railway.app"
railway variables set MPESA_SHORTCODE="174379"
railway variables set MPESA_PASSKEY="bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
railway variables set MPESA_CONSUMER_KEY="TeIIPGyP9AjpDcPlUSFymg0DALFmHbG4naKccawZKXKgGNgr"
railway variables set MPESA_CONSUMER_SECRET="AaxVYKXvYD8yJBpGmsmIDqZmBAFWdRbIcj9GhOnpdIfhhnGUSgesP5nSoe89SlwE"
railway variables set EMAIL_HOST="smtp.gmail.com"
railway variables set EMAIL_PORT="587"
railway variables set EMAIL_USE_TLS="True"

echo ✅ All variables set! Railway will now redeploy automatically.
pause
