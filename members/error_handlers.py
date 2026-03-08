"""
Custom error handling views for better user experience and developer debugging
"""
import logging
import traceback
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404

logger = logging.getLogger(__name__)

def custom_404(request, exception):
    """Custom 404 handler"""
    logger.warning(f"404 Error: {request.path} - {exception}")
    
    # If user is staff, show developer error page
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'errors/developer_404.html', {
            'error': exception,
            'path': request.path,
            'user': request.user,
        }, status=404)
    
    # Regular users get redirected to dashboard
    return redirect('admin_dashboard')

def custom_500(request):
    """Custom 500 handler"""
    logger.error(f"500 Error: {request.path}", exc_info=True)
    
    # Get the actual exception
    exc_info = traceback.format_exc()
    
    # If user is staff, show developer error page
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'errors/developer_500.html', {
            'error': exc_info,
            'path': request.path,
            'user': request.user,
        }, status=500)
    
    # Regular users get redirected to dashboard
    return redirect('admin_dashboard')

def custom_403(request, exception):
    """Custom 403 handler"""
    logger.warning(f"403 Error: {request.path} - User: {request.user} - {exception}")
    
    # If user is staff, show developer error page
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'errors/developer_403.html', {
            'error': exception,
            'path': request.path,
            'user': request.user,
        }, status=403)
    
    # Regular users get redirected to dashboard
    return redirect('admin_dashboard')

def custom_permission_denied(request, exception):
    """Custom permission denied handler"""
    logger.warning(f"Permission Denied: {request.path} - User: {request.user} - {exception}")
    
    # If user is staff, show developer error page
    if request.user.is_authenticated and request.user.is_staff:
        return render(request, 'errors/developer_403.html', {
            'error': exception,
            'path': request.path,
            'user': request.user,
        }, status=403)
    
    # Regular users get redirected to dashboard
    return redirect('admin_dashboard')
