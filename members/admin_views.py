from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator
from .admin_config import SystemConfiguration, RoomOverride, DivisionOverride, UnitOverride
from .admin_forms import (
    SystemConfigurationForm, 
    RoomOverrideForm, 
    DivisionOverrideForm, 
    UnitOverrideForm,
    ManualAssignmentForm
)
from .models import Member, Room, Unit


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def system_configuration(request):
    """Manage global system configuration"""
    config = SystemConfiguration.get_config()
    
    if request.method == 'POST':
        form = SystemConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'System configuration updated successfully!')
            return redirect('system_configuration')
    else:
        form = SystemConfigurationForm(instance=config)
    
    # Get current statistics
    total_members = Member.objects.count()
    total_rooms = Room.objects.count()
    total_units = Unit.objects.count()
    
    # Calculate utilization statistics
    full_rooms = sum(1 for room in Room.objects.all() if room.is_full)
    full_units = sum(1 for unit in Unit.objects.all() if unit.is_full)
    
    context = {
        'form': form,
        'config': config,
        'total_members': total_members,
        'total_rooms': total_rooms,
        'total_units': total_units,
        'utilization': {
            'members': (total_members / config.total_capacity * 100) if config.total_capacity > 0 else 0,
            'rooms': full_rooms,
            'units': full_units,
        }
    }
    
    return render(request, 'members/admin/system_configuration.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def room_overrides(request):
    """Manage room capacity overrides"""
    overrides = RoomOverride.objects.select_related('room').all()
    
    if request.method == 'POST':
        form = RoomOverrideForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Room capacity override added successfully!')
            return redirect('room_overrides')
    else:
        form = RoomOverrideForm()
    
    paginator = Paginator(overrides, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'overrides': page_obj,
        'total_overrides': overrides.count(),
    }
    
    return render(request, 'members/admin/room_overrides.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def delete_room_override(request, pk):
    """Delete a room capacity override"""
    override = get_object_or_404(RoomOverride, pk=pk)
    room_name = override.room.name
    override.delete()
    messages.success(request, f'Room capacity override for {room_name} deleted successfully!')
    return redirect('room_overrides')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def division_overrides(request):
    """Manage division capacity overrides"""
    overrides = DivisionOverride.objects.all()
    
    if request.method == 'POST':
        form = DivisionOverrideForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Division capacity override added successfully!')
            return redirect('division_overrides')
    else:
        form = DivisionOverrideForm()
    
    paginator = Paginator(overrides, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'overrides': page_obj,
        'total_overrides': overrides.count(),
    }
    
    return render(request, 'members/admin/division_overrides.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def delete_division_override(request, pk):
    """Delete a division capacity override"""
    override = get_object_or_404(DivisionOverride, pk=pk)
    division_num = override.division_number
    override.delete()
    messages.success(request, f'Division capacity override for Division {division_num} deleted successfully!')
    return redirect('division_overrides')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def unit_overrides(request):
    """Manage unit capacity overrides"""
    overrides = UnitOverride.objects.select_related('unit').all()
    
    if request.method == 'POST':
        form = UnitOverrideForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Unit capacity override added successfully!')
            return redirect('unit_overrides')
    else:
        form = UnitOverrideForm()
    
    paginator = Paginator(overrides, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'overrides': page_obj,
        'total_overrides': overrides.count(),
    }
    
    return render(request, 'members/admin/unit_overrides.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def delete_unit_override(request, pk):
    """Delete a unit capacity override"""
    override = get_object_or_404(UnitOverride, pk=pk)
    unit_name = override.unit.name
    override.delete()
    messages.success(request, f'Unit capacity override for {unit_name} deleted successfully!')
    return redirect('unit_overrides')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def manual_assignment(request):
    """Manually assign members to rooms, divisions, and units"""
    if request.method == 'POST':
        form = ManualAssignmentForm(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            room = form.cleaned_data['room']
            division = form.cleaned_data['division']
            unit = form.cleaned_data['unit']
            
            with transaction.atomic():
                # Update member assignments
                if room:
                    member.room = room
                if division:
                    member.division = division
                if unit:
                    member.unit = unit
                
                member.save()
                
                messages.success(
                    request, 
                    f'Member {member.first_name} {member.last_name} assigned successfully!'
                )
            
            return redirect('manual_assignment')
    else:
        form = ManualAssignmentForm()
    
    # Get assignment statistics
    members = Member.objects.all()
    total_members = members.count()
    assigned_to_rooms = members.filter(room__isnull=False).count()
    assigned_to_divisions = members.filter(division__isnull=False).count()
    assigned_to_units = members.filter(unit__isnull=False).count()
    
    context = {
        'form': form,
        'members': members,
        'stats': {
            'total_members': total_members,
            'assigned_to_rooms': assigned_to_rooms,
            'assigned_to_divisions': assigned_to_divisions,
            'assigned_to_units': assigned_to_units,
            'unassigned_rooms': total_members - assigned_to_rooms,
            'unassigned_divisions': total_members - assigned_to_divisions,
            'unassigned_units': total_members - assigned_to_units,
        }
    }
    
    return render(request, 'members/admin/manual_assignment.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='my_members')
def bulk_reassignment(request):
    """Bulk reassign all members based on current configuration"""
    if request.method == 'POST':
        config = SystemConfiguration.get_config()
        
        with transaction.atomic():
            # Clear all current assignments
            Member.objects.update(room=None, division=None, unit=None)
            
            # Reassign all members
            for member in Member.objects.all():
                member.assign_room(save=False)
                member.assign_division(save=False) 
                member.assign_unit(save=False)
                member.save()
        
        messages.success(request, 'All members have been reassigned based on current configuration!')
        return redirect('bulk_reassignment')
    
    context = {
        'config': SystemConfiguration.get_config(),
        'total_members': Member.objects.count(),
    }
    
    return render(request, 'members/admin/bulk_reassignment.html', context)
