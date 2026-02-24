from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        
        # List of URLs that don't require authentication
        public_urls = [
            reverse('login'),
            reverse('password_reset'),
            reverse('password_reset_done'),
            reverse('password_reset_confirm', kwargs={'uidb64': '123', 'token': '123'}).replace('123', '123'),  # Just to get the URL pattern
            reverse('password_reset_complete'),
            reverse('signup'),
            reverse('activate', kwargs={'uidb64': '123', 'token': '123'}).replace('123', '123'),  # For account activation
        ]
        
        # Allow access to static and media files
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return self.get_response(request)
            
        # Allow access to admin site
        if request.path.startswith('/admin/'):
            return self.get_response(request)
        
        # Allow access to public URLs and authenticated users
        if request.path in public_urls or request.user.is_authenticated:
            return self.get_response(request)
            
        # Redirect to login page for all other cases
        return redirect('login')
        
        response = self.get_response(request)
        return response
