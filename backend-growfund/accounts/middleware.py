from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
import json

class AdminSecurityMiddleware:
    """
    Middleware to secure admin routes and ensure proper authentication
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if accessing admin routes
        if request.path.startswith('/admin/'):
            # Allow login page and static files
            if (request.path == '/admin/login/' or 
                request.path.startswith('/admin/jsi18n/') or
                request.path.startswith('/static/') or
                request.path.startswith('/media/')):
                return self.get_response(request)
            
            # Check if user is authenticated and is staff
            if not request.user.is_authenticated:
                return redirect('/admin/login/')
            
            if not request.user.is_staff:
                return redirect('/admin/login/')
                
            # Additional security: Check if user has admin permissions
            if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
                return redirect('/admin/login/')
        
        # Check API admin routes
        if request.path.startswith('/api/admin/'):
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, status=401)
            
            if not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Admin access required',
                    'code': 'ADMIN_REQUIRED'
                }, status=403)
        
        response = self.get_response(request)
        return response