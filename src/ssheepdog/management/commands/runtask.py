from django.core.management.base import BaseCommand
from ssheepdog.tasks import sync

class Command(BaseCommand):
    def handle(self, *args, **options):
        sync.delay()

