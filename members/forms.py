# # # members/forms.py
# # from django import forms
# # from .models import Member, MembershipClass

# # class MemberForm(forms.ModelForm):
# #     class Meta:
# #         model = Member
# #         fields = [
# #             'first_name', 
# #             'last_name', 
# #             'email', 
# #             'phone_number', 
# #             'address', 
# #             'date_of_birth', 
# #             'picture', 
# #             'status', 
# #             'relationship', 
# #             'membership_class',
# #         ]
# # members/forms.py
# from django import forms
# from django.conf import settings

# # from members.views import send_welcome_email
# from .models import Member, Visitor
# # from .models import WorshipServiceAttendance, EventAttendance, SmallGroupAttendance



# from django import forms
# from .models import Member

# class MemberForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         fields = '__all__'  # Or specify individual fields if you prefer
#         widgets = {
#             'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
#             'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}),
#             'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Address'}),
#             'guardian_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Name'}),
#             'guardian_phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Guardian Phone Number'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'gender': forms.Select(attrs={'class': 'form-select'}),
#             'program_of_study': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Program of Study'}),
#             'level_of_study': forms.Select(attrs={'class': 'form-select'}),
#             'membership_class': forms.Select(attrs={'class': 'form-select'}),
#             'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#             'qr_code': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
#         }



# class MemberForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         exclude = ('qr_code',)

# class MemberEditForm(forms.ModelForm):
#     class Meta:
#         model = Member
#         exclude = ('qr_code',)  # Exclude the QR code field for editing

# # class AttendanceForm(forms.ModelForm):
# #     class Meta:
# #         model = WorshipServiceAttendance  # Adjust for EventAttendance or SmallGroupAttendance as needed
# #         fields = ['service_name', 'date']
# from .models import AttendanceSetting
# class AttendanceSettingForm(forms.ModelForm):
#     class Meta:
#         model = AttendanceSetting
#         fields = ['attendance_type', 'event_name', 'group_name']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['event_name'].widget.attrs.update({'class': 'form-control'})
#         self.fields['group_name'].widget.attrs.update({'class': 'form-control'})

#         #  # Set field visibility based on initial data
#         # attendance_type = self.initial.get('attendance_type')
#         # if attendance_type == 'event':
#         #     self.fields['group_name'].widget.attrs.update({'style': 'display: none;'})
#         # elif attendance_type == 'small_group':
#         #     self.fields['event_name'].widget.attrs.update({'style': 'display: none;'})
#         # else:
#         #     self.fields['event_name'].widget.attrs.update({'style': 'display: none;'})
#         #     self.fields['group_name'].widget.attrs.update({'style': 'display: none;'})

# class VisitorForm(forms.ModelForm):
#     class Meta:
#         model = Visitor
#         fields = ['first_name', 'last_name', 'email', 'phone_number']


# from django.core.mail import send_mail

# class FollowUpForm(forms.ModelForm):
#     class Meta:
#         model = Visitor
#         fields = ['follow_up_status']

#     def send_welcome_email_if_needed(self, visitor):
#         if not visitor.welcome_email_sent:
#             subject = "Welcome to Our Church"
#             message = f"Dear {visitor.first_name} {visitor.last_name},\n\nThank you for visiting our church! We are delighted to have you as our guest and look forward to welcoming you again."
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [visitor.email]

#             send_mail(subject, message, from_email, recipient_list)

#             visitor.welcome_email_sent = True
#             visitor.save()


from django import forms
from django.conf import settings
import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from .models import Member, Visitor, AttendanceSetting

class AdminSignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        'placeholder': 'Email address',
        'required': 'required'
    }))
    first_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        'placeholder': 'First name',
        'required': 'required'
    }))
    last_name = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
        'placeholder': 'Last name',
        'required': 'required'
    }))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500',
                'placeholder': 'Username',
                'required': 'required'
            }),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user

# Member Form for creating and editing members
class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'guardian_name', 'guardian_phone_number', 'date_of_birth', 'gender',
            'profession', 'allergies', 'nhis_number', 'church', 'district',
            'picture', 'vegetarian'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'required': 'required',
                'max': timezone.localdate().isoformat()
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter First Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Last Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Email',
                'required': 'required',
                'aria-required': 'true',
                'inputmode': 'email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Phone Number (include country code)',
                'required': 'required',
                'aria-required': 'true',
                'pattern': '\\+?[0-9 \\-]{7,15}',
                'inputmode': 'tel'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Address',
                'required': 'required'
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Guardian/Emergency Contact Name',
                'required': 'required'
            }),
            'guardian_phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Guardian/Emergency Contact Number',
                'required': 'required'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'profession': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Profession',
                'required': 'required'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'List any allergies or medical conditions',
                'rows': 3
            }),
            'nhis_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter NHIS Number'
            }),
            'church': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Church Name'
            }),
            'district': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter District'
            }),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input', 'aria-label': 'Vegetarian'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set required attribute for required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.widget.attrs['required'] = 'required'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Member.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('This email is already registered for another member.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '')
        if phone:
            # Normalize: allow +, spaces, dashes
            normalized = ''.join(ch for ch in phone if ch.isdigit())
            if len(normalized) < 7 or len(normalized) > 15:
                raise ValidationError('Enter a valid phone number with country code (7-15 digits).')
            return phone.strip()
        raise ValidationError('Phone number is required.')

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = timezone.localdate()
            if dob > today:
                raise ValidationError('Date of birth cannot be in the future.')
            # age sanity check
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 0 or age > 120:
                raise ValidationError('Please enter a realistic date of birth.')
        return dob

    def clean_picture(self):
        pic = self.cleaned_data.get('picture')
        if pic:
            # limit size to 3MB
            if hasattr(pic, 'size') and pic.size > 3 * 1024 * 1024:
                raise ValidationError('Profile picture must be smaller than 3MB.')
            # check content type if available
            content_type = getattr(pic, 'content_type', '')
            if content_type and content_type not in ('image/jpeg', 'image/png'):
                raise ValidationError('Allowed image formats: JPEG, PNG.')
        return pic

# Member form for editing (similar to MemberForm, but if needed, more specific widgets/fields could be added)
class MemberEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required attribute to all required fields
        for field_name, field in self.fields.items():
            if field_name != 'picture':  # Picture is optional
                field.required = True
                if field_name in ['first_name', 'last_name', 'email', 'phone_number', 'address', 
                                'guardian_name', 'guardian_phone_number', 'profession',
                                'nhis_number', 'church', 'district']:
                    self.fields[field_name].widget.attrs.update({
                        'required': 'required',
                        'aria-required': 'true'
                    })

    class Meta:
        model = Member
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 'address',
            'guardian_name', 'guardian_phone_number', 'date_of_birth',
            'gender', 'profession', 'picture', 'allergies',
            'nhis_number', 'church', 'district',
            'vegetarian'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'required': 'required',
                'aria-required': 'true'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'List any allergies or medical conditions',
                'rows': 3
            }),
            'nhis_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter NHIS Number'
            }),
            'church': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Church Name'
            }),
            'district': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter District'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter First Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Last Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Email',
                'required': 'required',
                'aria-required': 'true'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Phone Number',
                'required': 'required',
                'aria-required': 'true'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Full Address',
                'rows': 2,
                'required': 'required',
                'aria-required': 'true'
            }),
            'guardian_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Guardian/Emergency Contact Name',
                'required': 'required',
                'aria-required': 'true'
            }),
            'guardian_phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Guardian/Emergency Contact Number',
                'required': 'required',
                'aria-required': 'true'
            }),
            'specialization': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all',
                'placeholder': 'Enter Specialization',
                'required': 'required',
                'aria-required': 'true'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'level_of_profession': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all bg-white',
                'required': 'required',
                'aria-required': 'true'
            }),
            'picture': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100'
            }),
            'vegetarian': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make the qr_code field readonly in the form
        if 'qr_code' in self.fields:
            self.fields['qr_code'].widget.attrs['readonly'] = True

# Attendance setting form for events or small group attendance
class AttendanceSettingForm(forms.ModelForm):
    class Meta:
        model = AttendanceSetting
        fields = ['attendance_type', 'event_name', 'group_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['group_name'].widget.attrs.update({'class': 'form-control'})

# Visitor Form
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            # 'follow_up_status': forms.TextInput(attrs={'class': 'form-control'}),
        }
# Follow-up form for visitor follow-up
class FollowUpForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['follow_up_status']

    def send_welcome_email_if_needed(self, visitor):
        if not visitor.welcome_email_sent:
            subject = "Welcome to Our Church"
            message = f"Dear {visitor.first_name} {visitor.last_name},\n\nThank you for visiting our church! We are delighted to have you as our guest and look forward to welcoming you again."
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [visitor.email]

            send_mail(subject, message, from_email, recipient_list)

            visitor.welcome_email_sent = True
            visitor.save()
