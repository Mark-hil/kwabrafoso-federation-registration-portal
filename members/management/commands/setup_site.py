from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup the default site with the correct domain from settings'

    def handle(self, *args, **options):
        if not hasattr(settings, 'SITE_DOMAIN') or not hasattr(settings, 'SITE_NAME'):
            self.stdout.write(
                self.style.ERROR('SITE_DOMAIN and SITE_NAME must be defined in settings')
            )
            return

        try:
            site = Site.objects.get_current()
            if site.domain != settings.SITE_DOMAIN or site.name != settings.SITE_NAME:
                site.domain = settings.SITE_DOMAIN
                site.name = settings.SITE_NAME
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Site updated: {settings.SITE_DOMAIN} - {settings.SITE_NAME}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Site already configured: {settings.SITE_DOMAIN} - {settings.SITE_NAME}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating site: {e}')
            )
