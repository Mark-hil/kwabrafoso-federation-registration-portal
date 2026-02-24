from django.core.management.base import BaseCommand
from members.models import Member, Room
import random
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate the database with 100 test members and assign rooms and divisions'

    def handle(self, *args, **options):
        first_names = ['John', 'Jane', 'Michael', 'Emily', 'David', 'Sarah', 'Robert', 'Lisa', 
                      'William', 'Jennifer', 'James', 'Elizabeth', 'Joseph', 'Maria', 'Thomas']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']
        
        professions = ['Teacher', 'Engineer', 'Doctor', 'Lawyer', 'Business Owner', 
                      'Artist', 'Scientist', 'Mathematician', 'Historian', 'Psychologist']
        
        # Create rooms if they don't exist
        if not Room.objects.exists():
            self.stdout.write("Creating rooms...")
            constellations = ['Andromeda', 'Aquarius', 'Aries', 'Cancer', 'Capricorn', 'Gemini', 
                            'Leo', 'Libra', 'Pisces', 'Sagittarius', 'Scorpio', 'Taurus', 'Virgo']
            
            for constellation in constellations:
                Room.objects.create(name=constellation, capacity=40)
        
        self.stdout.write("Creating test members...")
        rooms = list(Room.objects.all())
        
        for i in range(1, 101):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
            
            # Create member with required fields first
            member = Member(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=f"233{random.randint(200000000, 299999999)}",
                address=f"{random.randint(1, 1000)} {random.choice(['Main', 'Oak', 'Pine', 'Maple', 'Cedar'])} St",
                guardian_name=f"Guardian {last_name}",
                guardian_phone_number=f"233{random.randint(200000000, 299999999)}",
                date_of_birth=date.today() - timedelta(days=random.randint(18*365, 70*365)),
                gender=random.choice(['male', 'female']),
                profession=random.choice(professions),
                allergies="None" if random.random() > 0.1 else "Peanuts, Dairy",
                nhis_number=f"NHIS{random.randint(1000000, 9999999)}",
                church=random.choice(['Central', 'North', 'South', 'East', 'West']),
                district=random.choice(['Accra', 'Kumasi', 'Tamale', 'Cape Coast', 'Takoradi'])
            )
            
            # Save the member first to get an ID
            member.save()
            
            # Now explicitly assign room and division
            try:
                # This will also assign a division
                member.assign_room(save=True)
                
                # Double-check division was assigned
                if not member.division:
                    member.assign_division(save=True)
                    self.stdout.write(f"Assigned division {member.division} to member {member.id} in post-processing")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error assigning room to member {member.id}: {str(e)}"))
            
            if i % 10 == 0:
                self.stdout.write(f"Created {i} members...")
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {i} test members with rooms and divisions'))