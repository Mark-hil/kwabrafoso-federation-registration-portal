from django.db import models
from django.core.exceptions import ValidationError

class SystemConfiguration(models.Model):
    """Global system configuration for member assignment rules"""
    
    # Division settings
    total_divisions = models.PositiveSmallIntegerField(
        default=5,
        help_text="Total number of divisions for member assignment"
    )
    members_per_division = models.PositiveSmallIntegerField(
        default=20,
        help_text="Target number of members per division"
    )
    
    # Unit settings
    units_per_division = models.PositiveSmallIntegerField(
        default=2,
        help_text="Number of units per division"
    )
    members_per_unit = models.PositiveSmallIntegerField(
        default=10,
        help_text="Maximum number of members per unit"
    )
    
    # Room settings
    default_room_capacity = models.PositiveSmallIntegerField(
        default=20,
        help_text="Default capacity for new rooms"
    )
    
    # Assignment rules
    enable_auto_assignment = models.BooleanField(
        default=True,
        help_text="Enable automatic room/division/unit assignment for new members"
    )
    balance_by_church = models.BooleanField(
        default=True,
        help_text="Balance members across rooms/divisions based on church"
    )
    balance_by_district = models.BooleanField(
        default=True,
        help_text="Balance members across rooms/divisions based on district"
    )
    balance_by_gender = models.BooleanField(
        default=True,
        help_text="Separate rooms by gender when possible"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
    
    def __str__(self):
        return f"Configuration - {self.total_divisions} divisions, {self.members_per_unit} per unit"
    
    def clean(self):
        """Validate configuration values"""
        if self.total_divisions < 1:
            raise ValidationError("Total divisions must be at least 1")
        
        if self.members_per_division < 1:
            raise ValidationError("Members per division must be at least 1")
        
        if self.units_per_division < 1:
            raise ValidationError("Units per division must be at least 1")
        
        if self.members_per_unit < 1:
            raise ValidationError("Members per unit must be at least 1")
        
        # Check if division capacity makes sense with unit capacity
        if self.members_per_division < self.units_per_division * self.members_per_unit:
            raise ValidationError(
                f"Division capacity ({self.members_per_division}) cannot be less than "
                f"total unit capacity ({self.units_per_division} × {self.members_per_unit} = {self.units_per_division * self.members_per_unit})"
            )
    
    @classmethod
    def get_config(cls):
        """Get or create the system configuration"""
        config, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'total_divisions': 5,
                'members_per_division': 20,
                'units_per_division': 2,
                'members_per_unit': 10,
                'default_room_capacity': 20,
                'enable_auto_assignment': True,
                'balance_by_church': True,
                'balance_by_district': True,
                'balance_by_gender': True,
            }
        )
        return config
    
    @property
    def total_capacity(self):
        """Calculate total system capacity"""
        return self.total_divisions * self.members_per_division
    
    @property
    def total_units(self):
        """Calculate total number of units"""
        return self.total_divisions * self.units_per_division


class RoomOverride(models.Model):
    """Override capacity for specific rooms"""
    
    room = models.OneToOneField(
        'Room', 
        on_delete=models.CASCADE,
        related_name='capacity_override'
    )
    custom_capacity = models.PositiveSmallIntegerField(
        help_text="Custom capacity for this room (overrides system default)"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for capacity override"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Room Capacity Override"
        verbose_name_plural = "Room Capacity Overrides"
    
    def __str__(self):
        return f"{self.room.name}: {self.custom_capacity} capacity"
    
    def clean(self):
        if self.custom_capacity < 1:
            raise ValidationError("Custom capacity must be at least 1")


class DivisionOverride(models.Model):
    """Override capacity for specific divisions"""
    
    division_number = models.PositiveSmallIntegerField(
        help_text="Division number (1-based)"
    )
    custom_capacity = models.PositiveSmallIntegerField(
        help_text="Custom capacity for this division"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for capacity override"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Division Capacity Override"
        verbose_name_plural = "Division Capacity Overrides"
        unique_together = ['division_number']
    
    def __str__(self):
        return f"Division {self.division_number}: {self.custom_capacity} capacity"
    
    def clean(self):
        if self.division_number < 1:
            raise ValidationError("Division number must be at least 1")
        
        if self.custom_capacity < 1:
            raise ValidationError("Custom capacity must be at least 1")


class UnitOverride(models.Model):
    """Override capacity for specific units"""
    
    unit = models.OneToOneField(
        'Unit',
        on_delete=models.CASCADE,
        related_name='capacity_override'
    )
    custom_capacity = models.PositiveSmallIntegerField(
        help_text="Custom capacity for this unit"
    )
    reason = models.TextField(
        blank=True,
        help_text="Reason for capacity override"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Unit Capacity Override"
        verbose_name_plural = "Unit Capacity Overrides"
    
    def __str__(self):
        return f"{self.unit.name}: {self.custom_capacity} capacity"
    
    def clean(self):
        if self.custom_capacity < 1:
            raise ValidationError("Custom capacity must be at least 1")
