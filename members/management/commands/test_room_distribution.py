from django.core.management.base import BaseCommand
from members.models import Member, Room
from django.db.models import Count
import random

class Command(BaseCommand):
    help = 'Test room distribution with sample data'

    def handle(self, *args, **options):
        # Clear existing data for testing
        Member.objects.all().delete()
        Room.objects.all().delete()
        
        # Create test data
        churches = ['Grace', 'Bethel', 'Zion', 'Emmanuel', 'Redeemed']
        districts = ['North', 'South', 'East', 'West', 'Central']
        
        # Create 100 test members
        for i in range(1, 101):
            church = random.choice(churches)
            district = random.choice(districts)
            
            member = Member.objects.create(
                first_name=f"Test{i}",
                last_name=f"Member{i}",
                email=f"test{i}@example.com",
                address=f"{i} Test St",
                guardian_name=f"Guardian {i}",
                gender=random.choice(['male', 'female']),
                profession=f"Profession {i}",
                church=church,
                district=district,
                # Other required fields...
            )
            
            # Assign room will be called automatically by the save() method
            
            if i % 20 == 0:
                self.stdout.write(f"Created {i} members...")
        
        # Print distribution report
        self.print_distribution_report()
    
    def print_distribution_report(self):
        self.stdout.write("\n" + "="*50)
        self.stdout.write("ROOM DISTRIBUTION REPORT")
        self.stdout.write("="*50)
        
        # Get all rooms with their members
        rooms = Room.objects.prefetch_related('members').all()
        
        for room in rooms:
            members = room.members.all()
            church_distribution = members.values('church').annotate(count=Count('church')).order_by('-count')
            district_distribution = members.values('district').annotate(count=Count('district')).order_by('-count')
            
            self.stdout.write(f"\nRoom: {room.name} ({len(members)} members)")
            
            self.stdout.write("\nChurch Distribution:")
            for item in church_distribution:
                self.stdout.write(f"  {item['church']}: {item['count']} members")
                
            self.stdout.write("\nDistrict Distribution:")
            for item in district_distribution:
                self.stdout.write(f"  {item['district']}: {item['district']} members")
            
            self.stdout.write("\n" + "-"*50)
            
        # Print summary
        total_rooms = rooms.count()
        total_members = Member.objects.count()
        avg_members = total_members / total_rooms if total_rooms > 0 else 0
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("SUMMARY")
        self.stdout.write("="*50)
        self.stdout.write(f"Total Rooms: {total_rooms}")
        self.stdout.write(f"Total Members: {total_members}")
        self.stdout.write(f"Average Members per Room: {avg_members:.2f}")
