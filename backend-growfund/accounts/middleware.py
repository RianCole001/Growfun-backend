from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class AdminSecurityMiddleware:
    """
    Middleware to secure admin routes and ensure proper authentication.
    Uses JWT authentication directly since DRF auth hasn't run yet at middleware level.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def _get_jwt_user(self, request):
        """Attempt to authenticate the request via JWT. Returns user or None."""
        try:
            jwt_auth = JWTAuthentication()
            result = jwt_auth.authenticate(request)
            if result is not None:
                return result[0]  # (user, token) tuple
        except (InvalidToken, TokenError, Exception):
            pass
        return None

    def __call__(self, request):
        # Secure Django admin panel (session-based, handled by Django itself)
        if request.path.startswith('/admin/'):
            if (request.path == '/admin/login/' or
                    request.path.startswith('/admin/jsi18n/') or
                    request.path.startswith('/static/') or
                    request.path.startswith('/media/')):
                return self.get_response(request)

            if not request.user.is_authenticated:
                return redirect('/admin/login/')
            if not request.user.is_staff:
                return redirect('/admin/login/')
            if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
                return redirect('/admin/login/')

        # Secure API admin routes — must authenticate via JWT here
        if request.path.startswith('/api/admin/'):
            user = self._get_jwt_user(request)

            if user is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'AUTH_REQUIRED'
                }, status=401)

            if not (user.is_staff or user.is_superuser):
                return JsonResponse({
                    'success': False,
                    'error': 'Admin access required',
                    'code': 'ADMIN_REQUIRED'
                }, status=403)

        return self.get_response(request)