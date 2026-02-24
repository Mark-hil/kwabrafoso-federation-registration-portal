from django.core.management.base import BaseCommand
from members.models import Member
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix division assignments for all members'

    def handle(self, *args, **options):
        members = Member.objects.all()
        total = members.count()
        
        self.stdout.write(f'Processing {total} members...')
        
        updated = 0
        with transaction.atomic():
            for member in members:
                # First assign a room if not assigned
                if not member.room:
                    member.assign_room(save=False)
                
                # Then assign division
                if not member.division:
                    member.assign_division(save=False)
                
                # Save only if either room or division was updated
                if member.room or member.division:
                    member.save(update_fields=['room', 'division'])
                    updated += 1
                
                if updated % 10 == 0 and updated > 0:
                    self.stdout.write(f'Processed {updated}/{total} members...')
        
        # Verify the results
        unassigned = Member.objects.filter(division__isnull=True).count()
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {updated} members. {unassigned} members still have no division.'))
        
        # Show distribution
        from django.db.models import Count
        distribution = Member.objects.values('division').annotate(count=Count('id')).order_by('division')
        self.stdout.write('\nDivision distribution:')
        for item in distribution:
            self.stdout.write(f"Division {item['division']}: {item['count']} members")
