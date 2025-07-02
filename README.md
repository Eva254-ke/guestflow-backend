# GuestFlow Backend API

A production-ready Django REST API for multi-tenant hotel/Airbnb management system with MongoDB Atlas integration and **Linktree-style microsites** for each property.

## 🚀 Features

- **Multi-Tenant Architecture**: Hotels, Airbnbs, resorts with isolated data
- **Microsite System**: Each property gets its own branded microsite (like Linktree)
  - `https://luxury-resort.yourdomain.com/` - Custom subdomain microsites
  - `https://yourdomain.com/hotel/luxury-resort/` - Path-based microsites
  - Custom branding, colors, and social media integration
- **Custom User Management**: Role-based access (Super Admin, Hotel Admin, Staff, Customers)
- **Hybrid Database**: Django ORM for authentication + MongoDB Atlas for business data
- **Room Management**: Rooms, pricing, availability, images, amenities
- **Booking System**: Full booking lifecycle with status tracking
- **Payment Integration**: M-Pesa integration ready
- **Admin Panel**: Beautiful Django admin with role-based filtering
- **API Ready**: RESTful endpoints for frontend integration
- **Production Security**: CORS, CSRF, environment variables, static files

## 🛠️ Tech Stack

- **Backend**: Django 5.2.3, Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production), MongoDB Atlas
- **Authentication**: Custom User Model with JWT support
- **File Storage**: WhiteNoise for static files, support for cloud storage
- **Deployment**: Railway, Heroku, Render ready

## 📋 Prerequisites

- Python 3.12+
- MongoDB Atlas account
- Git

## 🔧 Local Development Setup

### 1. Clone & Setup

```bash
git clone https://github.com/Eva254-ke/guestflow-backend.git
cd guestflow-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MONGODB_URI=your-mongodb-atlas-uri
MONGODB_NAME=guestflow
MONGODB_USERNAME=your-username
MONGODB_PASSWORD=your-password

CORS_ALLOWED_ORIGINS=http://localhost:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000
```

### 3. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/admin/

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

### Hotels & Microsites
- `GET /api/hotels/` - List hotels
- `POST /api/hotels/` - Create hotel
- `GET /api/hotels/{slug}/` - Hotel details by slug
- `PUT /api/hotels/{id}/` - Update hotel
- `GET /api/hotels/{slug}/microsite/` - Get microsite data
- `GET /{hotel-slug}/` - Public microsite view

### Rooms
- `GET /api/rooms/` - List rooms
- `POST /api/rooms/` - Create room
- `GET /api/rooms/{id}/` - Room details
- `PUT /api/rooms/{id}/` - Update room
- `GET /api/hotels/{slug}/rooms/` - Hotel's rooms

### Bookings
- `GET /api/bookings/` - List bookings
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/{id}/` - Booking details
- `PUT /api/bookings/{id}/` - Update booking status

## 🏨 Microsite Features (Linktree-style)

Each hotel/property gets its own branded microsite with:

### URL Patterns
```
Custom Subdomain: https://luxury-beach-resort.yourdomain.com/
Path-based: https://yourdomain.com/hotel/luxury-beach-resort/
Booking: https://luxury-beach-resort.yourdomain.com/book/
Gallery: https://luxury-beach-resort.yourdomain.com/gallery/
```

### Microsite Components
- **Custom Branding**: Logo, colors, fonts, cover images
- **Property Info**: Description, amenities, location, contact
- **Room Gallery**: Image galleries with pricing
- **Direct Booking**: Integrated booking system
- **Social Media**: Links to Instagram, Facebook, TikTok, etc.
- **Contact Integration**: WhatsApp, phone, email buttons
- **SEO Optimized**: Meta tags, structured data
- **Mobile Responsive**: Perfect on all devices

### Microsite Model Fields
```python
# Branding
custom_domain = models.CharField()  # e.g., 'luxury-resort.com'
brand_color_primary = models.CharField()  # #FF6B6B
brand_color_secondary = models.CharField()  # #4ECDC4
custom_css = models.TextField()  # Additional styling

# Social Media
instagram_url = models.URLField()
facebook_url = models.URLField()
tiktok_url = models.URLField()
twitter_url = models.URLField()
whatsapp_number = models.CharField()

# SEO
meta_title = models.CharField()
meta_description = models.TextField()
meta_keywords = models.CharField()
```

## 🏗️ Models Overview

### Core Models
- **Hotel**: Property management (hotels, Airbnbs, resorts)
- **CustomUser**: Extended user model with roles
- **Room**: Room management with pricing and availability
- **Booking**: Booking lifecycle management
- **Payment**: Payment processing and tracking

### User Roles
- **Super Admin**: Full system access
- **Hotel Admin**: Manage specific hotel
- **Hotel Staff**: Limited hotel operations
- **Customer**: Make bookings
- **Guest**: Browse properties

## 🚀 Deployment

### Docker Deployment (Recommended) 🐳

#### Local Docker Testing
```bash
# Build and run with Docker
docker build -t guestflow-backend .
docker run -p 8000:8000 --env-file .env guestflow-backend

# Or use Docker Compose
docker-compose up --build
```

#### Railway with Docker

1. **Push to GitHub** (already done)
   ```bash
   git add .
   git commit -m "Add Docker configuration for deployment"
   git push origin main
   ```

2. **Deploy to Railway**
   - Railway will automatically detect `Dockerfile` and `railway.toml`
   - Uses Docker build instead of Nixpacks (faster, more reliable)
   - Health check at `/health/` endpoint
   - Auto-restart on failure

3. **Environment Variables** (same as before)
   ```env
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app,yourdomain.com,*.yourdomain.com
   # ... other variables
   ```

### Alternative: Railway (Nixpacks)

1. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/Eva254-ke/guestflow-backend.git
   git branch -M main
   git push -u origin main
   ```

2. **Deploy to Railway**
   - Go to [Railway.app](https://railway.app)
   - Connect GitHub repository: `Eva254-ke/guestflow-backend`
   - Railway auto-detects Django and uses `requirements_deploy.txt`
   - Set environment variables in Railway dashboard

3. **Custom Domain Setup** (for microsites)
   - Add your domain in Railway
   - Configure wildcard DNS: `*.yourdomain.com` → Railway app
   - Enable SSL certificates

### Environment Variables for Production

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=*.railway.app,yourdomain.com,*.yourdomain.com
MONGODB_URI=your-mongodb-atlas-uri
MONGODB_NAME=guestflow
MONGODB_USERNAME=your-username
MONGODB_PASSWORD=your-password

# Microsite Configuration
MAIN_DOMAIN=yourdomain.com
ENABLE_SUBDOMAINS=True

# CORS for microsites
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://*.yourdomain.com
```

### Heroku

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

## 📁 Project Structure

```
guestflow-backend/
├── guestflow_project/          # Django project settings
├── users/                      # User management app
├── rentals/                    # Room/property management
├── bookings/                   # Booking system
├── static/                     # Static files
├── mediafiles/                 # Media files
├── requirements.txt            # Dependencies
├── requirements_deploy.txt     # Production dependencies
├── Procfile                    # Deployment config
├── runtime.txt                 # Python version
└── manage.py                   # Django management
```

## 🔐 Security Features

- Environment-based configuration
- CORS protection
- CSRF protection
- Role-based access control
- Input validation
- SQL injection protection
- XSS protection

## 🧪 Testing

```bash
python manage.py test
```

## 📖 Documentation

- Django Admin: `/admin/`
- API Documentation: `/api/docs/` (when implemented)
- Health Check: `/health/`

## 🤝 Contributing

1. Fork the repository: `https://github.com/Eva254-ke/guestflow-backend`
2. Create feature branch: `git checkout -b feature/microsite-enhancement`
3. Commit changes: `git commit -am 'Add microsite custom branding'`
4. Push branch: `git push origin feature/microsite-enhancement`
5. Submit pull request

### Code Review Guidelines
- **Microsite Features**: Ensure new microsite features are mobile-responsive
- **Multi-tenancy**: Verify data isolation between properties
- **Security**: All user inputs must be validated and sanitized
- **Performance**: Database queries should be optimized for scale
- **Testing**: Include tests for new endpoints and models

## 📄 License

This project is licensed under the MIT License.

## 👥 Team

- **Lead Developer**: Eva254-ke
- **Backend Architecture**: Django + MongoDB Atlas + Railway
- **Frontend Integration**: React (separate repository)
- **Microsite System**: Linktree-style property websites

## 🔗 Related Repositories

- **Frontend**: [guestflow-frontend](https://github.com/Eva254-ke/guestflow-frontend) (Coming Soon)
- **Mobile App**: [guestflow-mobile](https://github.com/Eva254-ke/guestflow-mobile) (Future)

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/Eva254-ke/guestflow-backend/issues)
- **Feature Requests**: Use the feature request template
- **Security Issues**: Email security@yourdomain.com

---

**GuestFlow Backend** - Powering the future of hospitality management with beautiful microsites 🏨✨  
**Repository**: https://github.com/Eva254-ke/guestflow-backend  
**Deployment**: Railway.app
