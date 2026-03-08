from django import forms
from django.core.exceptions import ValidationError
from .admin_config import SystemConfiguration, RoomOverride, DivisionOverride, UnitOverride
from .models import Room, Unit


class SystemConfigurationForm(forms.ModelForm):
    class Meta:
        model = SystemConfiguration
        fields = [
            'total_divisions',
            'members_per_division', 
            'units_per_division',
            'members_per_unit',
            'default_room_capacity',
            'enable_auto_assignment',
            'balance_by_church',
            'balance_by_district',
            'balance_by_gender',
        ]
        widgets = {
            'total_divisions': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'members_per_division': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'units_per_division': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'members_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'default_room_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'enable_auto_assignment': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balance_by_church': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balance_by_district': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'balance_by_gender': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        total_divisions = cleaned_data.get('total_divisions')
        members_per_division = cleaned_data.get('members_per_division')
        units_per_division = cleaned_data.get('units_per_division')
        members_per_unit = cleaned_data.get('members_per_unit')
        
        # Validate division vs unit capacity
        if members_per_division < units_per_division * members_per_unit:
            raise ValidationError(
                f"Division capacity ({members_per_division}) cannot be less than "
                f"total unit capacity ({units_per_division} × {members_per_unit} = {units_per_division * members_per_unit})"
            )
        
        return cleaned_data


class RoomOverrideForm(forms.ModelForm):
    class Meta:
        model = RoomOverride
        fields = ['room', 'custom_capacity', 'reason']
        widgets = {
            'room': forms.Select(attrs={'class': 'form-control'}),
            'custom_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter rooms that don't already have overrides
        existing_override_rooms = RoomOverride.objects.values_list('room_id', flat=True)
        self.fields['room'].queryset = Room.objects.exclude(id__in=existing_override_rooms)


class DivisionOverrideForm(forms.ModelForm):
    class Meta:
        model = DivisionOverride
        fields = ['division_number', 'custom_capacity', 'reason']
        widgets = {
            'division_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'custom_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        config = SystemConfiguration.get_config()
        
        # Limit division numbers to current system configuration
        self.fields['division_number'].widget.attrs['max'] = config.total_divisions


class UnitOverrideForm(forms.ModelForm):
    class Meta:
        model = UnitOverride
        fields = ['unit', 'custom_capacity', 'reason']
        widgets = {
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'custom_capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter units that don't already have overrides
        existing_override_units = UnitOverride.objects.values_list('unit_id', flat=True)
        self.fields['unit'].queryset = Unit.objects.exclude(id__in=existing_override_units)


class ManualAssignmentForm(forms.Form):
    """Form for manually assigning members to rooms, divisions, and units"""
    
    member = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        to_field_name='id'
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    division = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Member
        self.fields['member'].queryset = Member.objects.all()
        
        # Set division max based on current configuration
        config = SystemConfiguration.get_config()
        self.fields['division'].widget.attrs['max'] = config.total_divisions
        
        # Customize member field labels
        self.fields['member'].label_from_instance = lambda obj: f"{obj.first_name} {obj.last_name} ({obj.church or 'Unknown Church'})"
        
        # Add custom styling classes to form fields
        self.fields['member'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 text-gray-700 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-300 hover:bg-white hover:shadow-md'
        })
        self.fields['room'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 text-gray-700 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-300 hover:bg-white hover:shadow-md'
        })
        self.fields['division'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 text-gray-700 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-all duration-300 hover:bg-white hover:shadow-md'
        })
        self.fields['unit'].widget.attrs.update({
            'class': 'w-full pl-10 pr-4 py-3 text-gray-700 bg-gray-50 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all duration-300 hover:bg-white hover:shadow-md'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        
        division = cleaned_data.get('division')
        unit = cleaned_data.get('unit')
        
        # Validate that unit belongs to the specified division
        if unit and division and unit.division != division:
            from .models import Unit
            available_units = Unit.objects.filter(division=division).values_list('name', flat=True)
            if available_units:
                units_list = ', '.join(available_units)
                raise ValidationError(
                    f"Unit '{unit.name}' belongs to Division {unit.division}. "
                    f"Either select Division {unit.division} or choose a different unit. "
                    f"Available units for Division {division}: {units_list}"
                )
            else:
                raise ValidationError(
                    f"Unit '{unit.name}' belongs to Division {unit.division}. "
                    f"Either select Division {unit.division} or choose a different unit. "
                    f"No units available for Division {division}"
                )
        
        return cleaned_data
