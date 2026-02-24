from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME

def admin_required(view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is an admin (is_staff=True).
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator