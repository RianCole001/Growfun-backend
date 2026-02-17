from django.http import JsonResponse
from .models import PlatformSettings


class MaintenanceModeMiddleware:
    """
    Middleware to block non-admin users when maintenance mode is enabled
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip for admin users
        if request.user.is_authenticated and request.user.is_staff:
            return self.get_response(request)
        
        # Skip for public settings endpoint
        if request.path == '/api/settings/public/':
            return self.get_response(request)
        
        # Check maintenance mode
        try:
            settings = PlatformSettings.get_settings()
            if settings.maintenance_mode:
                return JsonResponse({
                    'success': False,
                    'error': 'Platform is under maintenance. Please try again later.',
                    'maintenanceMode': True
                }, status=503)
        except Exception as e:
            # If settings don't exist yet, allow access
            print(f"Maintenance mode check failed: {e}")
        
        return self.get_response(request)
