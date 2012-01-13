from django.core.management.base import BaseCommand, CommandError
from ssheepdog.sync import test_sync

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        test_sync()
        self.stdout.write("*********** I AM RUNNING ****************\n")
        print "Just curious what print does" # Probably not advised
        raise CommandError("But I was not finished yet")

