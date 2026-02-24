# members/models.py
from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
import random
from django.db.models import Count

class MembershipClass(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.members.count()}/{self.capacity})"
    
    @property
    def is_full(self):
        return self.members.count() >= self.capacity
    
    @classmethod
    def get_available_room(cls, member_church=None, member_district=None, member_gender=None):
        from django.db.models import Count, Q, F
        try:
            # Get all rooms that are not full
            available_rooms = cls.objects.annotate(
                member_count=Count('members'),
                same_church_count=Count('members', filter=Q(members__church=member_church) if member_church else Q(pk=None)),
                same_district_count=Count('members', filter=Q(members__district=member_district) if member_district else Q(pk=None)),
                diff_gender_count=Count('members', filter=~Q(members__gender=member_gender) if member_gender else Q(pk=None))
            ).filter(member_count__lt=F('capacity'))

            # If a member_gender is provided, exclude rooms where members of a different gender exist
            if member_gender:
                available_rooms = available_rooms.filter(diff_gender_count=0)
            
            if not available_rooms.exists():
                return None
                
            # Convert to list to evaluate the queryset
            available_rooms = list(available_rooms)
            
            # Sort rooms by:
            # 1. Fewest members from the same church
            # 2. Fewest members from the same district
            # 3. Fewest total members
            available_rooms.sort(key=lambda r: (
                r.same_church_count,
                r.same_district_count,
                r.member_count
            ))
            
            # Return the best room (first in the sorted list)
            return available_rooms[0] if available_rooms else None
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in get_available_room: {str(e)}")
            return None
    
    @classmethod
    def create_new_room(cls):
        try:
            # List of constellation and star names
            constellations = [
                'Andromeda', 'Antlia', 'Apus', 'Aquarius', 'Aquila', 'Ara', 'Aries', 'Auriga',
                'Boötes', 'Caelum', 'Camelopardalis', 'Cancer', 'Canes Venatici', 'Canis Major',
                'Capricornus', 'Carina', 'Cassiopeia', 'Centaurus', 'Cepheus', 'Cetus',
                'Chamaeleon', 'Circinus', 'Columba', 'Coma Berenices', 'Corona Australis',
                'Corona Borealis', 'Corvus', 'Crater', 'Crux', 'Cygnus', 'Delphinus', 'Dorado',
                'Draco', 'Equuleus', 'Eridanus', 'Fornax', 'Gemini', 'Grus', 'Hercules',
                'Horologium', 'Hydra', 'Hydrus', 'Indus', 'Lacerta', 'Leo', 'Leo Minor',
                'Lepus', 'Libra', 'Lupus', 'Lynx', 'Lyra', 'Mensa', 'Microscopium', 'Monoceros',
                'Musca', 'Norma', 'Octans', 'Ophiuchus', 'Orion', 'Pavo', 'Pegasus', 'Perseus',
                'Phoenix', 'Pictor', 'Pisces', 'Piscis Austrinus', 'Puppis', 'Pyxis', 'Reticulum',
                'Sagitta', 'Sagittarius', 'Scorpius', 'Sculptor', 'Scutum', 'Serpens', 'Sextans',
                'Taurus', 'Telescopium', 'Triangulum', 'Triangulum Australe', 'Tucana', 'Ursa Major',
                'Ursa Minor', 'Vela', 'Virgo', 'Volans', 'Vulpecula'
            ]
            
            stars = [
                'Sirius', 'Canopus', 'Alpha Centauri', 'Arcturus', 'Vega', 'Capella', 'Rigel',
                'Procyon', 'Achernar', 'Betelgeuse', 'Hadar', 'Altair', 'Acrux', 'Aldebaran',
                'Antares', 'Spica', 'Pollux', 'Fomalhaut', 'Deneb', 'Mimosa', 'Regulus',
                'Adhara', 'Castor', 'Gacrux', 'Bellatrix', 'Elnath', 'Miaplacidus', 'Alnilam',
                'Alnitak', 'Alhena', 'Polaris', 'Algol', 'Mira', 'Mizar', 'Alcor', 'Alcyone',
                'Pleione', 'Atlas', 'Electra', 'Maia', 'Merope', 'Taygeta', 'Celaeno', 'Asterope',
                'Almach', 'Mirach', 'Alpheratz', 'Hamal', 'Diphda', 'Menkar', 'Algiedi', 'Dabih',
                'Nashira', 'Deneb Algedi', 'Schedar', 'Caph', 'Ruchbah', 'Segin', 'Achird'
            ]
            
            # Get used room names in a single query
            used_names = set(cls.objects.values_list('name', flat=True))
            
            # First try single names (constellations and stars)
            all_names = set(constellations + stars)
            available_names = all_names - used_names
            
            # If no single names available, try combinations
            if not available_names:
                available_names = {
                    f"{c}-{s}" 
                    for c in constellations 
                    for s in stars
                    if f"{c}-{s}" not in used_names
                }
            
            if not available_names:
                raise ValueError("No available room names left!")
                
            name = random.choice(list(available_names))
            return cls.objects.create(name=name)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in create_new_room: {str(e)}")
            # Try a fallback name with a random number if all else fails
            try:
                return cls.objects.create(name=f"Room-{random.randint(1000, 9999)}")
            except Exception as fallback_error:
                logger.error(f"Fallback room creation also failed: {str(fallback_error)}")
                raise


class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=25, blank=True)
    address = models.CharField(max_length=200)
    guardian_name = models.CharField(max_length=100)
    guardian_phone_number = models.CharField(max_length=25, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    # active = models.BooleanField(default=True)
    picture = models.ImageField(upload_to='member_pictures/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    # relationship = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='family_members')
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    # MEMBERSHIP_CLASS = [
    #     ('Milerites', 'Milerites'),
    #     ('Missionaries', 'Missionaries'),
    #     ('Patriachs', 'Patriachs'),
    #     ('Disciples', 'Disciples'),
    #     ('Soul Winners', 'Soul Winners'),
    #     ('Reminats', 'Reminats'),
    #     ('Pioneers', 'Pioneers'),
    #     ('Adventurers', 'Adventurers'),
    #     ('Baptismal', 'Baptismal'),
    # ]

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='')
    profession = models.CharField('Profession', max_length=100)
    # membership_class = models.CharField(max_length=20, choices=MEMBERSHIP_CLASS, default='')
    allergies = models.TextField('Allergies', blank=True, null=True, help_text='List any allergies or medical conditions')
    nhis_number = models.CharField('NHIS No.', max_length=20, blank=True, null=True)
    vegetarian = models.BooleanField('Vegetarian', default=False, help_text='Check if the member requires vegetarian meals')
    church = models.CharField('Church', max_length=100, blank=True, null=True)
    district = models.CharField('District', max_length=100, blank=True, null=True)
    qr_code = models.BinaryField(null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    division = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Division number (1-4)")
    
    def assign_division(self, save=True):
        """
        Assign this member to a division (1-4) with balanced distribution.
        Ensures no other members in the same room are in the same division,
        and limits the number of members from the same church/district in a division.
        """
        from django.db.models import Count, Q
        from collections import defaultdict

        if self.division:
            return self.division

        divisions = [1, 2, 3, 4]
        
        # Get divisions already used in this room
        used_divisions = set()
        if self.room:
            used_divisions = set(Member.objects.filter(
                room=self.room,
                division__isnull=False
            ).exclude(pk=self.pk).values_list('division', flat=True))

        # Get division counts for all divisions
        division_counts = {d: 0 for d in divisions}
        counts = Member.objects.values('division').annotate(
            count=Count('id')
        ).filter(division__isnull=False)

        for item in counts:
            division_counts[item['division']] = item['count']

        # Get church/district distribution in each division
        church_district_divisions = defaultdict(int)
        if self.church and self.district:
            # Count how many from same church/district are in each division
            church_district_counts = Member.objects.filter(
                church=self.church,
                district=self.district
            ).exclude(pk=self.pk).values('division').annotate(
                count=Count('id')
            )
            for item in church_district_counts:
                church_district_divisions[item['division']] = item['count']

        # Find available divisions (not used in this room)
        available_divisions = [d for d in divisions if d not in used_divisions]
        
        # If no available divisions, use all divisions (shouldn't happen with 4 divisions)
        if not available_divisions:
            available_divisions = divisions

        # Score each division (lower is better)
        division_scores = {}
        for div in available_divisions:
            # Base score is the current division count
            score = division_counts.get(div, 0)
            
            # Add penalty for church/district concentration
            if div in church_district_divisions:
                # Increase score based on how many from same church/district are already in this division
                score += church_district_divisions[div] * 5  # 5x weight to prioritize spreading out same church/district
            
            division_scores[div] = score

        # Choose division with lowest score
        chosen_division = min(division_scores.items(), key=lambda x: x[1])[0]

        self.division = chosen_division

        if save:
            self.save(update_fields=['division'])
        
        return chosen_division
        
    def assign_room(self, save=True):
        """
        Assign this member to a room with available space, trying to distribute
        members from the same church/district across different rooms.
        If save is True, the member will be saved automatically.
        """
        # If already assigned to a room that's not full, keep it
        if self.room and not self.room.is_full:
            # Ensure division is assigned
            if not self.division:
                self.assign_division(save=save)
            return self.room
            
        # First try to find a room with good distribution
        room = Room.get_available_room(
            member_church=self.church,
            member_district=self.district,
            member_gender=self.gender
        )

        # If no room found with good distribution, try any available room
        if not room:
            room = Room.get_available_room(member_gender=self.gender)
            
        # If still no room, create a new one
        if not room:
            room = Room.create_new_room()
        
        # Assign the room
        self.room = room
        
        # Always assign a new division when room changes
        self.division = None
        self.assign_division(save=False)
        
        # Only save if explicitly requested to prevent recursion
        if save:
            update_fields = ['room']
            if self.division:
                update_fields.append('division')
            self.save(update_fields=update_fields)
            
        return room
        
    def save(self, *args, **kwargs):
        # Check if this is a new member before saving
        is_new = self._state.adding
        
        # If this is a new member, we'll handle room assignment after the initial save
        if is_new:
            # First save the member to get an ID
            super().save(*args, **kwargs)
            
            # Now assign a room if not already assigned
            if not self.room:
                try:
                    self.assign_room(save=False)
                    # Save just the room assignment to avoid recursion
                    super().save(update_fields=['room'])
                except Exception as e:
                    # Log the error but don't fail the save
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error assigning room to member {self.id}: {str(e)}")
        else:
            # For existing members, just save normally
            super().save(*args, **kwargs)

# def generate_qr_code_for_attendance(member):
#     # Fetch the active attendance setting
#     active_setting = AttendanceSetting.objects.filter(is_active=True).first()
    
#     if active_setting:
#         qr_data = f"http://127.0.0.1:8000/scan-attendance/?member_id={member.id}&attendance_type={active_setting.attendance_type}"
        
#         if active_setting.attendance_type == 'event':
#             qr_data += f"&event_name={active_setting.event_name}"
#         elif active_setting.attendance_type == 'small_group':
#             qr_data += f"&group_name={active_setting.group_name}"

#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(qr_data)
#         qr.make(fit=True)
        
#         img = qr.make_image(fill='black', back_color='white')
#         buffer = BytesIO()
#         img.save(buffer, format='PNG')
#         qr_code_file = ContentFile(buffer.getvalue(), 'attendance_qrcode.png')
        
#         return qr_code_file

#     return None
from django.http import HttpResponseForbidden
def generate_qr_code_for_attendance(member):
    active_setting = AttendanceSetting.objects.filter(is_active=True).first()

    if not active_setting:
        # Return None instead of HttpResponseForbidden to avoid errors in the view
        return None
    
    # Generate a unique token for this QR code
    import uuid
    from django.core.cache import cache
    
    # Create a token that's valid for the configured duration
    token = str(uuid.uuid4())
    cache_key = f'qr_token_{member.id}_{token}'
    from django.conf import settings
    from datetime import datetime
    # Store token data with last_used date (no expiration)
    token_data = {
        'valid': True,
        'last_used': None,  # Will be set on first use
        'member_id': member.id  # Store member ID for cleanup
    }
    # Store without expiration (permanent until deleted)
    cache.set(cache_key, token_data, timeout=None)
    
    # Hardcode the production URL for QR codes
    from urllib.parse import quote_plus
    base_url = 'https://attendance-tracking-system-5d9n.onrender.com'
    # Include both member ID and name in the QR code with proper URL encoding
    full_name = f"{member.first_name} {member.last_name}"
    qr_data = f"{base_url}/scan-attendance/?member_id={member.id}&name={quote_plus(full_name)}&token={token}"
    print(f"[DEBUG] Generated QR code URL: {qr_data}")  # Debug log
    
    # Create QR code with higher error correction and larger size
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Higher error correction
        box_size=12,  # Slightly larger box size
        border=6,     # Larger border
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image with high contrast
    img = qr.make_image(
        fill_color='black',
        back_color='white',
        image_factory=None,  # Use default image factory
    )
    
    # Ensure the QR code is large enough to be scanned
    size = (img.size[0] * 2, img.size[1] * 2)  # Double the size
    img = img.resize(size, resample=0)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG', quality=100)
    qr_code_file = ContentFile(buffer.getvalue(), f'attendance_qrcode_{member.id}.png')
    
    return qr_code_file
    # def save(self, *args, **kwargs):
    #     # Generate QR code
    #     qr = qrcode.QRCode(
    #         version=1,
    #         error_correction=qrcode.constants.ERROR_CORRECT_L,
    #         box_size=10,
    #         border=4,
    #     )
    #     qr.add_data(f'{self.first_name} {self.last_name}\nEmail: {self.email}\nPhone: {self.phone_number}')
    #     qr.make(fit=True)

    #     img = qr.make_image(fill='black', back_color='white')
    #     canvas = Image.new('RGB', (290, 290), 'white')
    #     draw = ImageDraw.Draw(canvas)
    #     canvas.paste(img)
    #     fname = f'qr_code-{self.first_name}{self.last_name}.png'
    #     buffer = BytesIO()
    #     canvas.save(buffer, 'PNG')
    #     self.qr_code.save(fname, File(buffer), save=False)
    #     canvas.close()

    #     super().save(*args, **kwargs)

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"
    
    

# class WorshipServiceAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     date = models.DateField()
#     service_name = models.CharField(max_length=255)
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.service_name} on {self.date}"

# class EventAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     event_name = models.CharField(max_length=255)
#     event_date = models.DateField()
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.event_name} on {self.event_date}"

# class SmallGroupAttendance(models.Model):
#     member = models.ForeignKey('Member', on_delete=models.CASCADE)
#     group_name = models.CharField(max_length=255)
#     meeting_date = models.DateField()
#     checked_in = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.member} - {self.group_name} on {self.meeting_date}"
    


from django.db import models
from django.utils import timezone
from datetime import time


# class WorshipService(models.Model):
#     name = models.CharField(max_length=100)
#     date = models.DateTimeField()
#     location = models.CharField(max_length=200)

#     def __str__(self):
#         return self.name

# class Event(models.Model):
#     name = models.CharField(max_length=100)
#     date = models.DateTimeField()
#     location = models.CharField(max_length=200)

#     def __str__(self):
#         return self.name

# class Attendance(models.Model):
#     ATTENDANCE_TYPE_CHOICES = [
#         ('Worship Service', 'Worship Service'),
#         ('Event', 'Event'),
#         ('Small Group', 'Small Group'),
#     ]
#     member = models.ForeignKey(Member, on_delete=models.CASCADE)
#     attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPE_CHOICES)
#     worship_service = models.ForeignKey(WorshipService, on_delete=models.SET_NULL, null=True, blank=True)
#     event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)
#     date = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.member} - {self.attendance_type} on {self.date}"
    
class AttendanceSetting(models.Model):
    ATTENDANCE_TYPES = [
        ('lecture_hours', 'Lecture Hours'),
        ('event', 'Event'),
        # ('small_group', 'Small Group'),
    ]

    attendance_type = models.CharField(max_length=20, choices=ATTENDANCE_TYPES)
    event_name = models.CharField(max_length=100, blank=True, null=True)
    group_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(default=timezone.now)
    is_active = models.BooleanField(default=False)  # To mark if this setting is currently in use
    # time_of_attendance = models.TimeField(default=None, null=True, blank=True)  # Store the actual time

class WorshipServiceAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    # Other fields...

class EventAttendance(models.Model):
    setting = models.ForeignKey(AttendanceSetting, on_delete=models.CASCADE, null=True, blank=True)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    event_name = models.CharField(max_length=255)
    
    # Other fields...

class SmallGroupAttendance(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    group_name = models.CharField(max_length=255)
    setting = models.ForeignKey(AttendanceSetting, on_delete=models.CASCADE, null=True, blank=True)
    # Other fields...



    # def __str__(self):
    #     return f"{self.attendance_type} - {self.date}"

    def __str__(self):
        return f"{self.attendance_type} on {self.date} - {'Active' if self.is_active else 'Inactive'}"
    
    # def __str__(self):
    #     return f"{self.get_attendance_type_display()} - Active: {self.is_active}"
    
    # def __str__(self):
    #     return f"Active Setting: {self.attendance_type}"

    

    class Meta:
        verbose_name = "Attendance Setting"
        verbose_name_plural = "Attendance Settings"



from django.utils import timezone

class Visitor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    visit_date = models.DateField(auto_now_add=True)
    follow_up_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('attended', 'Attended')
    ], default='pending')
    welcome_email_sent = models.BooleanField(default=False)  # New field
    # last_contacted = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
        
    def assign_room(self, save=True):
        """
        Assign this member to a room with available space.
        If save is True, the member will be saved automatically.
        """
        # If already assigned to a room that's not full, keep it
        if self.room and not self.room.is_full:
            return self.room
            
        # Try to find an available room
        room = Room.get_available_room()
        
        # If no available room, create a new one
        if not room:
            room = Room.create_new_room()
        
        # Assign the room
        self.room = room
        
        # Only save if explicitly requested to prevent recursion
        if save:
            self.save(update_fields=['room'])
            
        return room
        
    def save(self, *args, **kwargs):
        # Check if this is a new member before saving
        is_new = self._state.adding
        
        # If this is a new member, we'll handle room assignment after the initial save
        if is_new:
            # First save the member to get an ID
            super().save(*args, **kwargs)
            
            # Now assign a room if not already assigned
            if not self.room:
                try:
                    self.assign_room(save=False)
                    # Save just the room assignment to avoid recursion
                    super().save(update_fields=['room'])
                except Exception as e:
                    # Log the error but don't fail the save
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error assigning room to member {self.id}: {str(e)}")
        else:
            # For existing members, just save normally
            super().save(*args, **kwargs)
