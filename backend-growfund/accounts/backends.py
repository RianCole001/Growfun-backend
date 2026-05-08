"""
Custom authentication backend for email-based login
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using email instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email and password.
        
        Args:
            request: The HTTP request object
            username: Email address (we use 'username' param for compatibility)
            password: User password
            **kwargs: Additional keyword arguments (including 'email')
        
        Returns:
            User object if authentication succeeds, None otherwise
        """
        # Support both 'username' and 'email' parameters
        email = kwargs.get('email', username)
        
        if email is None or password is None:
            return None
        
        try:
            # Get user by email (case-insensitive)
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
        
        # Check password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID.
        
        Args:
            user_id: User's primary key
        
        Returns:
            User object if found, None otherwise
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        return user if self.user_can_authenticate(user) else None
