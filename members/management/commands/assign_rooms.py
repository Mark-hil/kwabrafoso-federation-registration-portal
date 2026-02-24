from django.core.management.base import BaseCommand
from members.models import Member, Room
import random

class Command(BaseCommand):
    help = 'Randomly assign all members to rooms'

    def handle(self, *args, **options):
        # Get all members without a room
        unassigned_members = Member.objects.filter(room__isnull=True)
        total_members = unassigned_members.count()
        
        if total_members == 0:
            self.stdout.write(self.style.SUCCESS('All members already have rooms assigned'))
            return
            
        self.stdout.write(f'Assigning {total_members} members to rooms...')
        
        assigned_count = 0
        for member in unassigned_members:
            # Get a random available room or create a new one if needed
            room = Room.get_available_room(member_gender=member.gender)
            if not room:
                room = Room.create_new_room()
                self.stdout.write(f'Created new room: {room.name}')
            
            # Assign member to the room
            member.room = room
            member.save()
            assigned_count += 1
            
            # Print progress
            if assigned_count % 10 == 0:
                self.stdout.write(f'Assigned {assigned_count}/{total_members} members...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully assigned {assigned_count} members to rooms')
        )
        
        # Print room statistics
        self.stdout.write('\nRoom assignments:')
        for room in Room.objects.all():
            self.stdout.write(f'{room.name}: {room.members.count()}/{room.capacity} members')
