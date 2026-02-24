from django.core.management.base import BaseCommand
from members.models import Member, Room
from django.db import models, transaction
from collections import defaultdict

class Command(BaseCommand):
    help = 'Balance members across all divisions evenly'

    def handle(self, *args, **options):
        # Get all members
        members = list(Member.objects.all().select_related('room').order_by('room__id'))
        total_members = len(members)
        
        if total_members == 0:
            self.stdout.write(self.style.SUCCESS('No members found'))
            return
            
        # Calculate target members per division
        divisions = [1, 2, 3, 4]
        target_per_division = total_members // len(divisions)
        remainder = total_members % len(divisions)
        
        self.stdout.write(f'Total members: {total_members}')
        self.stdout.write(f'Target per division: {target_per_division} (with {remainder} extra members)')
        
        # Get current division counts
        current_counts = Member.objects.values('division').annotate(
            count=models.Count('id')
        ).order_by('division')
        
        self.stdout.write('\nCurrent division counts:')
        for count in current_counts:
            self.stdout.write(f'Division {count["division"]}: {count["count"]} members')
        
        # Track room divisions and division counts
        room_divisions = defaultdict(set)  # {room_id: set(assigned_divisions)}
        division_counts = {d: 0 for d in divisions}  # Track division counts manually
        
        # First pass: assign divisions to members with rooms
        with transaction.atomic():
            # Reset all divisions
            Member.objects.all().update(division=None)
            
            # Process members in room order
            for member in members:
                available_divisions = set(divisions)
                
                # Remove divisions already used in this room
                if member.room_id:
                    available_divisions -= room_divisions[member.room_id]
                
                # If no available divisions, we need to reuse one
                if not available_divisions and member.room_id:
                    # Find the least used division in this room
                    used_divisions = room_divisions[member.room_id]
                    division_usage = {d: division_counts[d] for d in used_divisions}
                    chosen_division = min(division_usage.items(), key=lambda x: x[1])[0]
                else:
                    # Find the least used available division
                    available_division_counts = {d: division_counts[d] for d in available_divisions}
                    chosen_division = min(available_division_counts.items(), key=lambda x: x[1])[0]
                
                # Assign the division
                member.division = chosen_division
                member.save(update_fields=['division'])
                
                # Update our tracking
                if member.room_id:
                    room_divisions[member.room_id].add(chosen_division)
                division_counts[chosen_division] += 1
        
        # Final division counts
        final_counts = Member.objects.values('division').annotate(
            count=models.Count('id')
        ).order_by('division')
        
        self.stdout.write('\nFinal division counts:')
        for count in final_counts:
            self.stdout.write(f'Division {count["division"]}: {count["count"]} members')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully balanced {total_members} members across divisions'))