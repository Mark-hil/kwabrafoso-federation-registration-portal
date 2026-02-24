from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'class': 'form-control', 'placeholder': 'Enter your email'}),
        required=True,
        help_text=_("Required. Enter a valid email address.")
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email is already in use. Please use a different email address."))
        return email

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Email or Username"),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email or username'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if '@' in username:
            try:
                validate_email(username)
                user = User.objects.get(email__iexact=username)
                return user.username
            except User.DoesNotExist:
                pass
        return username
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = None
            # Try to authenticate with email first
            if '@' in username:
                try:
                    user = User.objects.get(email__iexact=username)
                    self.user_cache = authenticate(username=user.username, password=password)
                    if self.user_cache is not None:
                        try:
                            self.confirm_login_allowed(self.user_cache)
                        except forms.ValidationError as e:
                            # Check if the user is inactive
                            if not self.user_cache.is_active:
                                raise forms.ValidationError(
                                    _("This account is inactive. Please check your email to activate your account."),
                                    code='inactive',
                                )
                            raise
                except User.DoesNotExist:
                    pass
            
            # If email authentication failed, try with username
            if self.user_cache is None:
                self.user_cache = authenticate(username=username, password=password)
                if self.user_cache is None:
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
                else:
                    try:
                        self.confirm_login_allowed(self.user_cache)
                    except forms.ValidationError as e:
                        # Check if the user is inactive
                        if not self.user_cache.is_active:
                            raise forms.ValidationError(
                                _("This account is inactive. Please check your email to activate your account."),
                                code='inactive',
                            )
                        raise
        
        return self.cleaned_data
