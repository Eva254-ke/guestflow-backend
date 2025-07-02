from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

@method_decorator(csrf_exempt, name='dispatch')
class HealthCheckView(View):
    """Health check endpoint for Docker and deployment platforms"""
    
    def get(self, request):
        """Simple health check"""
        try:
            # You can add more sophisticated health checks here
            # like database connectivity, external service checks, etc.
            
            health_data = {
                "status": "healthy",
                "service": "GuestFlow Backend API",
                "version": "1.0.0",
                "timestamp": "2025-07-02",
                "database": "MongoDB Atlas",
                "features": [
                    "Multi-tenant hotel management",
                    "Linktree-style microsites",
                    "Role-based access control",
                    "M-Pesa payment integration"
                ]
            }
            
            return JsonResponse(health_data, status=200)
            
        except Exception as e:
            return JsonResponse({
                "status": "unhealthy",
                "error": str(e)
            }, status=500)

class APIInfoView(View):
    """API information endpoint"""
    
    def get(self, request):
        api_info = {
            "service": "GuestFlow Backend API",
            "version": "1.0.0",
            "description": "Multi-tenant hotel/Airbnb management system with Linktree-style microsites",
            "features": {
                "multi_tenant": "Hotels, Airbnbs, resorts with isolated data",
                "microsites": "Each property gets branded microsite like Linktree",
                "authentication": "Role-based access control",
                "database": "Hybrid Django ORM + MongoDB Atlas",
                "payments": "M-Pesa integration ready",
                "deployment": "Docker + Railway/Render ready"
            },
            "endpoints": {
                "admin": "/admin/",
                "health": "/health/",
                "api": "/api/",
                "hotels": "/api/hotels/",
                "rooms": "/api/rooms/",
                "bookings": "/api/bookings/"
            },
            "microsite_examples": [
                "https://luxury-resort.yourdomain.com/",
                "https://yourdomain.com/hotel/luxury-resort/"
            ],
            "github": "https://github.com/Eva254-ke/guestflow-backend",
            "deployment": "Railway.app + Docker"
        }
        
        return JsonResponse(api_info, status=200)
