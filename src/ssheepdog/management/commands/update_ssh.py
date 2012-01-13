from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        
                self.stdout.write('Successfully closed poll "%s"\n' % poll_id)

