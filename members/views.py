# members/views.py
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpResponseForbidden
from .decorators import admin_required
from django.contrib import messages
from .forms import AdminSignupForm
from .models import AttendanceSetting, Member, generate_qr_code_for_attendance
# from django.shortcuts import render
from .forms import FollowUpForm, MemberForm, MemberEditForm

from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import Member
from .utils.sms import send_sms
import csv
import json

from PIL import Image
import io
import logging
from django.conf import settings
import os

import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from .models import Member,  Visitor
from datetime import date
from django.db.models import Count

from .models import AttendanceSetting, Member, WorshipServiceAttendance, EventAttendance, SmallGroupAttendance
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404

from .models import AttendanceSetting
from .forms import AttendanceSettingForm

@login_required
def scanner(request):
    return render(request, 'members/scanner.html')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def member_list(request):
    from django.utils import timezone
    from datetime import timedelta
    from django.template.defaultfilters import register
    
    query = request.GET.get('q')
    page = request.GET.get('page', 1)
    per_page = int(request.GET.get('per_page', 10))
    
    # Base queryset
    if query:
        members = Member.objects.filter(
            first_name__icontains=query
        ) | Member.objects.filter(
            last_name__icontains=query
        ) | Member.objects.filter(
            email__icontains=query
        ) | Member.objects.filter(
            phone_number__icontains=query
        ) | Member.objects.filter(
            address__icontains=query
        )
    else:
        members = Member.objects.all()
    
    # Order by last name, then first name
    members = members.order_by('last_name', 'first_name')
    
    # Pagination
    paginator = Paginator(members, per_page)
    paginator.per_page = per_page  # Store per_page value for template
    
    try:
        members_page = paginator.page(page)
    except PageNotAnInteger:
        members_page = paginator.page(1)
    except EmptyPage:
        members_page = paginator.page(paginator.num_pages)
    
    # Handle AJAX requests for pagination
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Preprocess members for AJAX response
        for member in members_page:
            if member.allergies:
                member.allergies_list = [a.strip() for a in str(member.allergies).split(',') if a.strip()]
            else:
                member.allergies_list = []
                
        html = render_to_string('members/member_list_rows.html', {
            'members': members_page,
            'page_obj': members_page,
            'is_paginated': paginator.num_pages > 1,
            'paginator': paginator
        }, request=request)
        return HttpResponse(html)
    
    # Calculate statistics (using the base queryset to include all matching results)
    total_members = members.count()
    
    # Get the first day of the current month
    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = Member.objects.filter(date_joined__gte=first_day_of_month).count()
    
    # Get gender distribution for statistics
    gender_distribution = members.values('gender').annotate(count=Count('gender'))
    
    # Get unique church count
    church_count = members.exclude(church__isnull=True).exclude(church__exact='').values('church').distinct().count()
    
    # Preprocess members to add allergies_list to each member
    for member in members_page:
        if member.allergies:
            member.allergies_list = [a.strip() for a in str(member.allergies).split(',') if a.strip()]
        else:
            member.allergies_list = []
    
    context = {
        'members': members_page,
        'page_obj': members_page,  # For pagination template tags
        'is_paginated': paginator.num_pages > 1,
        'paginator': paginator,
        'member_count': total_members,
        'new_members': new_this_month,
        'gender_distribution': gender_distribution,
        'church_count': church_count,
    }
    
    return render(request, 'members/member_list.html', context)


# import qrcode
# from io import BytesIO
# from django.core.files.base import ContentFile

# def generate_qr_code_for_attendance(member):
#     qr_data = f"http://localhost:8000/track_attendance/?data=Member ID:{member.id}, Name:{member.first_name} {member.last_name}, Phone Number: {member.phone_number}, Membership Class: {member.membership_class}"
    
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_H,  # Adjust error correction level
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(qr_data)
#     qr.make(fit=True)
    
#     img = qr.make_image(fill='black', back_color='white')
#     buffer = BytesIO()
#     img.save(buffer, format='PNG')
#     qr_code_file = ContentFile(buffer.getvalue(), 'attendance_qrcode.png')
    
#     return qr_code_file


import logging

@login_required
def add_member(request):
    logger = logging.getLogger(__name__)
    logger.info("Add member view called")
    
    if request.method == 'POST':
        logger.info("POST request received")
        form = MemberForm(request.POST, request.FILES)
        logger.info(f"Form is bound: {form.is_bound}")
        
        if form.is_valid():
            logger.info("Form is valid")
            try:
                # Log form data for debugging
                logger.info(f"Form cleaned data: {form.cleaned_data}")
                
                # Create the member but don't save to DB yet
                member = form.save(commit=False)
                logger.info(f"Member instance created: {member}")
                
                # Save to get an ID
                member.save()
                logger.info(f"Member saved with ID: {member.id}")
                
                # Save many-to-many relationships if any
                form.save_m2m()
                logger.info("Many-to-many relationships saved")
                
                # Assign room and division
                logger.info("Assigning room and division...")
                member.assign_room(save=False)  # Don't save yet
                # Ensure division is assigned
                if not member.division:
                    member.assign_division(save=False)
                # Save both room and division
                member.save(update_fields=['room', 'division'])
                logger.info(f"Room assigned: {member.room}, Division: {member.division}")
                
                # Generate QR code
                logger.info("Generating QR code...")
                from .models import generate_qr_code_for_attendance
                try:
                    qr_code_file = generate_qr_code_for_attendance(member)
                    
                    if qr_code_file and hasattr(qr_code_file, 'read'):
                        logger.info("QR code generated, saving...")
                        member.qr_code = qr_code_file.read()
                        # Save QR code
                        member.save(update_fields=["qr_code"])
                    else:
                        logger.warning("No QR code generated, saving without QR code")
                        member.save()
                except Exception as e:
                    logger.error(f"Error generating QR code: {str(e)}")
                    # Save member without QR code if there's an error
                    member.save()
                
                # Send welcome SMS with room and division details
                try:
                    # Format the welcome message with emojis and clear sections
                    message = (
                        f"Welcome to Kwabrafoso Distict Youth Ministry!\n\n"
                        f"Dear {member.first_name} {member.last_name},\n\n"
                        f"Thank you for registering for the 2026 Annual Survival Camp! "
                        f"Here are your assigned room and division details:\n\n"
                        f"Room: {member.room.name if member.room else 'To be assigned'}\n"
                        f"Division: {member.division if member.division else 'To be assigned'}\n\n"
                        f"We look forward to seeing you at the camp!\n\n"
                        f"Best regards,\n"
                        f"Kwabrafoso District Youth Ministry Team"
                    )
                    
                    if member.phone_number:
                        sms_sent = send_sms(member.phone_number, message)
                        if sms_sent:
                            logger.info(f"Welcome SMS sent to {member.phone_number}")
                        else:
                            logger.warning(f"Failed to send welcome SMS to {member.phone_number}")
                except Exception as e:
                    logger.error(f"Error sending welcome SMS: {str(e)}")
                    # Don't fail the member creation if SMS fails
                
                logger.info("Member saved successfully, redirecting...")
                return redirect('member_list')
                
            except Exception as e:
                logger.error(f"Error creating member: {str(e)}", exc_info=True)
                # If anything fails, clean up and show error
                if 'member' in locals() and hasattr(member, 'pk') and member.pk:
                    try:
                        member.delete()
                        logger.info("Rolled back member creation due to error")
                    except Exception as delete_error:
                        logger.error(f"Error deleting member after failure: {str(delete_error)}")
                
                form.add_error(None, f'Error creating member: {str(e)}')
                return render(request, 'members/add_member.html', {'form': form})
        else:
            logger.warning(f"Form is invalid. Errors: {form.errors}")
    else:
        form = MemberForm()
        logger.info("Initial form created for GET request")
    
    return render(request, 'members/add_member.html', {'form': form})


@login_required
def edit_member(request, pk):
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberEditForm(request.POST, request.FILES, instance=member)
        
        if form.is_valid():
            try:
                member = form.save(commit=False)
                if 'picture' in request.FILES:
                    member.picture = request.FILES['picture']
                member.save()
                form.save_m2m()
                messages.success(request, 'Member updated successfully!')
                return redirect('member_list')
            except Exception as e:
                messages.error(request, f'Error updating member: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MemberEditForm(instance=member)
    
    return render(request, 'members/edit_member.html', {
        'form': form,
        'member': member,
        'title': f'Edit {member.first_name} {member.last_name}'
    })

from django.db import transaction
from django.contrib import messages

@login_required
def delete_member(request, pk):
    try:
        with transaction.atomic():
            member = get_object_or_404(Member, pk=pk)
            if request.method == 'POST':
                member.delete()
                messages.success(request, 'Member deleted successfully')
                return redirect('member_list')
            return render(request, 'members/delete_member.html', {'member': member})
    except Exception as e:
        messages.error(request, f'Error deleting member: {str(e)}')
        return redirect('member_list')


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='member_list')
def export_members_csv(request):
    # Create the HTTP response object with the CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=members.csv'

    writer = csv.writer(response)
    writer.writerow([
        'First Name', 'Last Name', 'Email', 'Phone Number', 'Profession',
        'Gender', 'Address', 'Date of Birth', 'Allergies', 'NHIS Number',
        'Church', 'District', 'Vegetarian', 'Guardian Name', 'Guardian Phone', 
        'Division', 'Room', 'Room Capacity'
    ])

    # Prefetch related room data to avoid N+1 queries
    members = Member.objects.select_related('room').all()
    
    for member in members:
        writer.writerow([
            member.first_name,
            member.last_name,
            member.email,
            member.phone_number or '',
            member.profession or '',
            member.get_gender_display(),
            member.address or '',
            member.date_of_birth.strftime('%Y-%m-%d') if member.date_of_birth else '',
            member.allergies or '',
            member.nhis_number or '',
            member.church or '',
            member.district or '',
            ('Yes' if member.vegetarian else 'No'),
            member.guardian_name or '',
            member.guardian_phone_number or '',
            f"Division {member.division}" if member.division else 'Unassigned',
            member.room.name if member.room else 'Unassigned',
            f"{member.room.members.count()}/{member.room.capacity}" if member.room else 'N/A'
        ])

    return response


@login_required
def track_attendance(request):
#     qr_code_data = request.GET.get('data')
#     if qr_code_data:
#         # Parse QR code data to extract member ID
#         member_id = qr_code_data.split(',')[0].split(':')[1].strip()
#         member = get_object_or_404(Member, id=member_id)

#         # Mark attendance
#         # Assuming you're tracking worship service attendance
#         WorshipServiceAttendance.objects.create(
#             member=member,
#             service_name='Sunday Service',
#             date=datetime.date.today()
#         )

#         return HttpResponse('Attendance recorded successfully.')
    
  return HttpResponse('Invalid QR code data.')




def attendance_report(request):
    # Fetch all attendance records
    worship_attendance = WorshipServiceAttendance.objects.all()
    event_attendance = EventAttendance.objects.all()
    small_group_attendance = SmallGroupAttendance.objects.all()

    context = {
        'worship_attendance': worship_attendance,
        'event_attendance': event_attendance,
        'small_group_attendance': small_group_attendance,
    }

    return render(request, 'members/attendance_report.html', context)





@login_required
def mark_attendance(request):
    # Initialize variables
    member_id = None
    
    # Debug logging
    print("\n" + "="*50)
    print("[DEBUG] mark_attendance called")
    print("-"*50)
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Raw GET params: {dict(request.GET)}")
    print(f"[DEBUG] Raw POST params: {dict(request.POST)}")
    
    # Try to get member_id and member_name from different sources
    member_name = None
    if request.method == 'GET':
        member_id = request.GET.get('member_id')
        member_name = request.GET.get('name')
    elif request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                member_id = data.get('member_id')
                member_name = data.get('member_name') or data.get('name')  # Try both 'member_name' and 'name' keys
                print(f"[DEBUG] JSON data: {data}")
            except json.JSONDecodeError as e:
                print(f"[DEBUG] JSON decode error: {str(e)}")
                return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
        else:
            member_id = request.POST.get('member_id')
            member_name = request.POST.get('member_name') or request.POST.get('name')
    
    # If name is URL-encoded, decode it
    if member_name and ('%' in member_name or '+' in member_name):
        from urllib.parse import unquote_plus
        member_name = unquote_plus(member_name)
    
    print(f"[DEBUG] After extraction - member_id: {member_id}, member_name: {member_name}")
    
    # If we have a member_id but no name, try to get the member from the database
    if member_id and not member_name:
        try:
            member = Member.objects.get(id=member_id)
            member_name = f"{member.first_name} {member.last_name}"
            print(f"[DEBUG] Fetched name from database: {member_name}")
        except (Member.DoesNotExist, ValueError):
            print(f"[DEBUG] Could not find member with ID {member_id}")
            pass
    
    # Debug output
    print(f"[DEBUG] Extracted member_id: {member_id} (type: {type(member_id)})")
    
    # Validate member_id
    if not member_id:
        return JsonResponse({
            'success': False,
            'message': 'Member ID is required.'
        }, status=400)
    
    # Convert member_id to integer if it's a string
    try:
        member_id = int(member_id)
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'Invalid member ID format. Must be a number.'
        }, status=400)
    
    try:
        # Get the member
        member = get_object_or_404(Member, id=member_id)
        
        # Check if there's an active attendance setting
        active_setting = AttendanceSetting.objects.filter(is_active=True).first()
        if not active_setting:
            return JsonResponse({
                'success': False,
                'message': 'No active attendance session found. Please set up an attendance type first.'
            }, status=400)
        
        # Check if attendance is already recorded for the member for today
        today = timezone.now().date()
        attendance_exists = False
        
        if active_setting.attendance_type == 'lecture_hours':
            attendance_exists = WorshipServiceAttendance.objects.filter(
                member=member, 
                date=today
            ).exists()
        elif active_setting.attendance_type == 'event':
            attendance_exists = EventAttendance.objects.filter(
                member=member, 
                setting=active_setting, 
                date=today
            ).exists()
        elif active_setting.attendance_type == 'small_group':
            attendance_exists = SmallGroupAttendance.objects.filter(
                member=member, 
                setting=active_setting, 
                date=today
            ).exists()

        if attendance_exists:
            return JsonResponse({
                'success': False, 
                'message': f'Attendance for {member.first_name} {member.last_name} has already been recorded for today.'
            })

        # Mark attendance if it doesn't already exist
        if active_setting.attendance_type == 'lecture_hours':
            WorshipServiceAttendance.objects.create(
                member=member, 
                date=today,
                time=timezone.now().time()
            )
            attendance_type = 'Lecture Hours'
        elif active_setting.attendance_type == 'event':
            EventAttendance.objects.create(
                member=member, 
                setting=active_setting, 
                date=today,
                time=timezone.now().time(),
                event_name=active_setting.event_name or 'General Event'
            )
            attendance_type = 'Event'
        elif active_setting.attendance_type == 'small_group':
            SmallGroupAttendance.objects.create(
                member=member, 
                setting=active_setting, 
                date=today,
                time=timezone.now().time(),
                group_name=active_setting.group_name or 'General Group'
            )
            attendance_type = 'Small Group'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid attendance type configured'
            }, status=400)

        # Use the name from the request if provided, otherwise use the one from the member record
        display_name = member_name or f'{member.first_name} {member.last_name}'
        
        return JsonResponse({
            'success': True, 
            'message': f'{attendance_type} attendance recorded for {display_name}!',
            'member_name': display_name,
            'attendance_type': attendance_type,
            'date': today.strftime('%Y-%m-%d'),
            'time': timezone.now().strftime('%H:%M:%S')
        })

    except Member.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Member not found.'
        }, status=404)
    except Exception as e:
        print(f"[ERROR] Error processing attendance: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Error processing attendance: {str(e)}'
        }, status=500)

def attendance_report(request):
    # Get the current date or use a date provided by the user
    today = timezone.now().date()
    start_date = request.GET.get('start_date', str(today))
    end_date = request.GET.get('end_date', str(today))
    
    # Convert dates from query parameters
    if 'reset' in request.GET:
        # Reset to the current date
        start_date = today
        end_date = today
    else:
        try:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
            # Ensure end_date is not before start_date
            if end_date < start_date:
                end_date = start_date
        except (ValueError, TypeError):
            start_date = today
            end_date = today

    # Calculate counts for each attendance type within the date range
    # For working hours (WorshipServiceAttendance)
    worship_service_count = WorshipServiceAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For events (EventAttendance)
    event_attendance_count = EventAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For small groups (SmallGroupAttendance)
    small_group_attendance_count = SmallGroupAttendance.objects.filter(
        date__range=[start_date, end_date]
    ).count()
    
    # For visitors
    visitor_count = Visitor.objects.filter(
        visit_date__range=[start_date, end_date]
    ).count()
    
    # Get unique member counts for each attendance type
    unique_members_working = Member.objects.filter(
        worshipserviceattendance__date__range=[start_date, end_date]
    ).distinct().count()
    
    unique_members_events = Member.objects.filter(
        eventattendance__date__range=[start_date, end_date]
    ).distinct().count()
    
    unique_members_groups = Member.objects.filter(
        smallgroupattendance__date__range=[start_date, end_date]
    ).distinct().count()

    # Pass the totals to the template
    context = {
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'small_group_attendance_count': small_group_attendance_count,
        'visitor_count': visitor_count,
        'unique_members_working': unique_members_working,
        'unique_members_events': unique_members_events,
        'unique_members_groups': unique_members_groups,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
    }

    return render(request, 'members/attendance_report.html', context)


@login_required
def export_attendance_report(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="detailed_attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Attendance Type', 'Member Name', 'Event/Group Name', 'Date', 'Time'])

    # Export Working Hours Attendance
    working_hours_attendance = WorshipServiceAttendance.objects.all()
    for record in working_hours_attendance:
        writer.writerow([
            'Lecture Hours',
            f"{record.member.first_name} {record.member.last_name}",
            "N/A",  # No event or group name for working hours
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    # Export Event Attendance
    event_attendance = EventAttendance.objects.all()
    for record in event_attendance:
        writer.writerow([
            'Event',
            f"{record.member.first_name} {record.member.last_name}",
            record.setting.event_name if record.setting else "N/A",
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    # Export Small Group Attendance
    small_group_attendance = SmallGroupAttendance.objects.all()
    for record in small_group_attendance:
        writer.writerow([
            'Small Group',
            f"{record.member.first_name} {record.member.last_name}",
            record.setting.group_name if record.setting else "N/A",
            record.date,
            record.time.strftime("%H:%M:%S") if record.time else "N/A"
        ])

    return response



@login_required
def set_attendance_type(request):
    if request.method == 'POST':
        form = AttendanceSettingForm(request.POST)
        if form.is_valid():
            setting = form.save(commit=False)
            # Deactivate all other settings
            AttendanceSetting.objects.update(is_active=False)
            setting.is_active = True
            setting.save()
            return redirect('scanner')  # Redirect to the settings page or another page
    else:
        form = AttendanceSettingForm()

    current_setting = AttendanceSetting.objects.filter(is_active=True).first()
    return render(request, 'members/set_attendance_type.html', {'form': form, 'current_setting': current_setting})


@login_required
@user_passes_test(lambda u: u.is_staff, login_url='member_list')
def print_badges(request):
    # Get all members with related room data
    members = Member.objects.select_related('room').all()
    
    # Prepare member data for the template
    member_data = []
    for member in members:
        # Create a unique identifier for the QR code
        qr_data = f"{member.id}:{member.first_name} {member.last_name}"
        
        member_data.append({
            'id': member.id,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'full_name': f"{member.first_name} {member.last_name}",
            'room': member.room.name if member.room else 'Unassigned',
            'division': f"Division {member.division}" if member.division else 'Unassigned',
            'allergies': member.allergies if member.allergies else 'None',
            'qr_data': qr_data,  # Add the properly formatted QR data
            'vegetarian': bool(member.vegetarian),
        })
    
    return render(request, 'members/print_badges.html', {'members': member_data})



@login_required
def view_qr_code(request, member_id):
    """Retrieve and serve the QR code from PostgreSQL as an image."""
    member = get_object_or_404(Member, id=member_id)

    # If no QR code stored at all, generate it now and persist
    if not member.qr_code:
        try:
            import qrcode
            from io import BytesIO
            import uuid
            from django.core.cache import cache
            
            # Generate a unique token for this QR code
            token = str(uuid.uuid4())
            cache_key = f'qr_token_{member.id}_{token}'
            
            # Store token data
            token_data = {
                'valid': True,
                'last_used': None,
                'member_id': member.id
            }
            cache.set(cache_key, token_data, timeout=None)
            
            # Create QR code with production URL and include member name
            from urllib.parse import quote_plus
            base_url = 'https://attendance-tracking-system-5d9n.onrender.com'
            full_name = f"{member.first_name} {member.last_name}"
            qr_data = f"{base_url}/scan-attendance/?member_id={member.id}&name={quote_plus(full_name)}&token={token}"
            
            # Generate QR code with high error correction
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=12,
                border=6,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create image with high contrast
            img = qr.make_image(fill_color='black', back_color='white')
            
            # Ensure the QR code is large enough to be scanned
            size = (img.size[0] * 2, img.size[1] * 2)
            img = img.resize(size, resample=0)
            
            # Save to buffer
            buffer = BytesIO()
            img.save(buffer, format='PNG', quality=100)
            image_data = buffer.getvalue()
            
            # Persist for future requests
            member.qr_code = image_data
            member.save(update_fields=["qr_code"])
            
            return HttpResponse(image_data, content_type="image/png")
            
        except Exception as regen_err:
            logging.error(f"Could not generate QR code for member {member.id}: {regen_err}")
            return HttpResponse("QR code not available", status=404)
            
    # If QR code exists, serve it directly
    return HttpResponse(member.qr_code, content_type="image/png")

    if member.qr_code:
        # `qr_code` can be stored either as raw binary (BinaryField) or as a file path/FileField.
        try:
            # Case 1: qr_code already holds raw bytes / memoryview
            if isinstance(member.qr_code, (bytes, bytearray, memoryview)):
                # Convert memoryview to bytes if necessary
                image_data = bytes(member.qr_code)
                # Directly serve bytes without re-processing to avoid potential PIL issues
                return HttpResponse(image_data, content_type="image/png")
            elif hasattr(member.qr_code, "url"):
                # If it's a Django FiewldFile with its own URL, simply redirect to it.
                return redirect(member.qr_code.url)
            else:
                # Case 2: qr_code is an ImageField/FileField (Django `File` object or path)
                # Ensure the file is opened and read into memory as bytes
                if hasattr(member.qr_code, "read"):
                    # Django File object
                    member.qr_code.open("rb")
                    image_data = member.qr_code.read()
                else:
                    # Plain filesystem path stored as string (may be relative to MEDIA_ROOT)
                    file_path = str(member.qr_code)
                    if not os.path.isabs(file_path):
                        file_path = os.path.join(settings.MEDIA_ROOT, file_path)

                    if not os.path.exists(file_path):
                        # File missing – regenerate QR code on the fly and persist so future lookups succeed.
                        try:
                            import qrcode
                            from io import BytesIO

                            # qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}"
                            qr = qrcode.QRCode(
                                version=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L,
                                box_size=10,
                                border=4,
                            )
                            # qr.add_data(qr_data)
                            qr.make(fit=True)
                            img = qr.make_image(fill='black', back_color='white')
                            buffer = BytesIO()
                            img.save(buffer, format='PNG')
                            image_data = buffer.getvalue()

                            # Save regenerated bytes back to member record
                            member.qr_code = image_data
                            member.save(update_fields=["qr_code"])
                        except Exception as regen_err:
                            logging.error(f"Could not regenerate QR code for member {member.id}: {regen_err}")
                            return HttpResponse("QR code file not found", status=404)
                    else:
                        with open(file_path, "rb") as f:
                            image_data = f.read()

            image = Image.open(io.BytesIO(image_data))
            response = HttpResponse(content_type="image/png")
            image.save(response, "PNG")
            return response
        except Exception as e:
            # Log the error
            logging.error(f"Error serving QR code: {e}")
            # Return a friendly message
            return HttpResponse("Unable to render QR code", status=500)
    else:
        return HttpResponse("No QR code available", status=404)


from .models import Visitor
from .forms import VisitorForm

@login_required
def add_visitor(request):
    if request.method == 'POST':
        form = VisitorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('visitor_list')
    else:
        form = VisitorForm()
    return render(request, 'visitors/add_visitor.html', {'form': form})

@login_required
def visitor_list(request):
    visitors = Visitor.objects.all()
    return render(request, 'visitors/visitor_list.html', {'visitors': visitors})


from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def send_welcome_email(visitor):
    subject = "Welcome to Our Church!"
    message = f"Dear {visitor.first_name},\n\nThank you for visiting us. We are glad to have you."
    recipient_list = [visitor.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)  



@login_required
def follow_up_visitor(request, pk):
    visitor = get_object_or_404(Visitor, pk=pk)
    
    if request.method == 'POST':
        form = FollowUpForm(request.POST, instance=visitor)
        if form.is_valid():
            visitor = form.save()
            form.send_welcome_email_if_needed(visitor)  # Call the method to send the email
            return redirect('visitor_list')
    else:
        form = FollowUpForm(instance=visitor)
    
    return render(request, 'visitors/follow_up_visitor.html', {'form': form})

@login_required
@admin_required
def admin_signup(request):
    """View for creating new admin accounts (superuser only)."""
    if request.method == 'POST':
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Successfully created admin account for {user.username}')
            return redirect('member_list')
    else:
        form = AdminSignupForm()
    
    return render(request, 'registration/admin_signup.html', {'form': form})

@login_required
def dashboard(request):
    from datetime import date, timedelta
    import json
    from django.db.models import Count
    
    # Get the total members, attendance, and visitors for today
    total_members = Member.objects.count()
    worship_service_count = WorshipServiceAttendance.objects.filter(date=date.today()).count()
    event_attendance_count = EventAttendance.objects.filter(date=date.today()).count()
    visitors_today = Visitor.objects.filter(visit_date=date.today()).count()
    
    # Generate trend data for the last 7 days
    trend_dates = []
    trend_data = []
    
    for i in range(6, -1, -1):
        current_date = date.today() - timedelta(days=i)
        total_attendance = (
            WorshipServiceAttendance.objects.filter(date=current_date).count() +
            EventAttendance.objects.filter(date=current_date).count()
        )
        trend_dates.append(current_date.strftime('%Y-%m-%d'))
        trend_data.append(total_attendance)

    context = {
        'total_members': total_members,
        'worship_service_count': worship_service_count,
        'event_attendance_count': event_attendance_count,
        'visitors_today': visitors_today,
        # pass Python lists so template can safely json_script them
        'trend_labels': trend_dates,
        'trend_data': trend_data,
        'user': request.user,  # Ensure user is in context
    }

    # Registrations by church - filter out empty/None values and add total
    registrations_by_church = list(Member.objects.exclude(church__isnull=True)
                                        .exclude(church__exact='')
                                        .values('church')
                                        .annotate(count=Count('id'))
                                        .order_by('-count'))
    
    # Calculate unknown church count
    unknown_church_count = Member.objects.filter(church__isnull=True) | Member.objects.filter(church__exact='')
    if unknown_church_count.exists():
        registrations_by_church.append({'church': None, 'count': unknown_church_count.count()})

    # Registrations by district - filter out empty/None values and add total
    registrations_by_district = list(Member.objects.exclude(district__isnull=True)
                                            .exclude(district__exact='')
                                            .values('district')
                                            .annotate(count=Count('id'))
                                            .order_by('-count'))
    
    # Calculate unknown district count
    unknown_district_count = Member.objects.filter(district__isnull=True) | Member.objects.filter(district__exact='')
    if unknown_district_count.exists():
        registrations_by_district.append({'district': None, 'count': unknown_district_count.count()})

    # Gender totals - ensure we count all members and handle case sensitivity
    gender_counts = {
        'male': Member.objects.filter(gender__iexact='male').count(),
        'female': Member.objects.filter(gender__iexact='female').count()
    }

    # Room allocation stats
    from .models import Room
    total_rooms = Room.objects.count()
    rooms_with_members = Room.objects.annotate(member_count=Count('members')).filter(member_count__gt=0).count()
    room_stats = list(Room.objects.annotate(member_count=Count('members')).values('name', 'member_count', 'capacity').order_by('-member_count'))

    # Add to context
    # compute occupancy percentage for template progress bars
    for r in room_stats:
        cap = r.get('capacity') or 0
        mem = r.get('member_count') or 0
        try:
            r['occupancy_pct'] = int((mem / cap) * 100) if cap > 0 else 0
        except Exception:
            r['occupancy_pct'] = 0

    # Add to context with proper serialization
    context.update({
        'registrations_by_church': registrations_by_church,
        'registrations_by_district': registrations_by_district,
        'gender_counts': gender_counts,
        'total_rooms': total_rooms,
        'rooms_with_members': rooms_with_members,
        'room_stats': room_stats,
        # Provide trend data as JSON strings for JS consumption
        'trend_labels': json.dumps(trend_dates),
        'trend_data': json.dumps(trend_data),
    })

    return render(request, 'members/dashboard.html', context)

# Authentication Views
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.shortcuts import redirect
from .authentication_forms import CustomUserCreationForm, EmailOrUsernameAuthenticationForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()

def activate(request, uidb64, token):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        logger.info(f"User found: {user.username}, is_active: {user.is_active}")
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Activation error: {str(e)}")
        messages.error(request, 'Activation link is invalid!')
        return redirect('login')

    if user is not None:
        token_valid = default_token_generator.check_token(user, token)
        logger.info(f"Token valid for user {user.username}: {token_valid}")
        
        if token_valid:
            if not user.is_active:
                user.is_active = True
                user.save()
                # Refresh from database to confirm
                user.refresh_from_db()
                logger.info(f"User {user.username} activated. is_active after save: {user.is_active}")
                messages.success(request, 'Thank you for your email confirmation. Now you can login to your account.')
            else:
                messages.info(request, 'Your account is already activated. You can login now.')
            return redirect('login')
        else:
            # Token is invalid or expired
            logger.warning(f"Invalid token for user {user.username}")
            messages.error(request, 'Activation link is invalid or has expired. Please request a new activation email.')
            return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid!')
        return redirect('login')

def resend_activation_email(request):
    """Allow users to request a new activation email."""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, 'This account is already active. You can login directly.')
                return redirect('login')
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Kfoso D AYM account.'
            message = render_to_string('auth/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            email_obj = EmailMessage(
                mail_subject, message, to=[user.email]
            )
            try:
                email_obj.send()
                messages.success(request, 'Activation email sent. Please check your email.')
            except Exception as e:
                messages.error(request, f'Could not send email. Error: {str(e)}')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return redirect('login')
    
    return render(request, 'auth/resend_activation.html')

@admin_required
def signup_view(request):
    """View for creating new user accounts (admin only)."""
    import logging
    logger = logging.getLogger(__name__)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save user as active first, then deactivate after token generation
            user = form.save(commit=True)
            logger.info(f"User created (active): {user.username}, pk: {user.pk}")
            
            # Generate token while user is active
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            logger.info(f"Token generated for user {user.username}: {token[:20]}...")
            
            # Now deactivate the user
            user.is_active = True
            user.save()
            logger.info(f"User deactivated: {user.username}")
            
            # Send verification email
            current_site = get_current_site(request)
            mail_subject = 'Activate your Kfoso D AYM account.'
            
            message = render_to_string('auth/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            try:
                email.send()
                logger.info(f"Activation email sent to {to_email}")
                messages.success(request, 'New user account created. Verification email sent. Please ask them to check their email to complete registration.')
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
                messages.warning(request, f'New user account created, but email could not be sent. Error: {str(e)}')
            return redirect('member_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = EmailOrUsernameAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.POST.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            # Show form errors instead of generic message
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = EmailOrUsernameAuthenticationForm()
    
    # Add next parameter to the context if it exists in the URL
    next_url = request.GET.get('next', '')
    return render(request, 'auth/login.html', {
        'form': form,
        'next': next_url
    })

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')