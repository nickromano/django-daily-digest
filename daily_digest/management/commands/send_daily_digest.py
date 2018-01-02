from django.core.management.base import BaseCommand
from daily_digest.utils import send_daily_digest


class Command(BaseCommand):
    help = 'Send daily digest email.'

    def success_message(self, message):
        if hasattr(self.style, 'SUCCESS'):
            self.stdout.write(self.style.SUCCESS(message))
        else:
            # Django 1.8
            self.stdout.write(self.style.MIGRATE_SUCCESS(message))

    def handle(self, *args, **options):
        send_daily_digest()

        self.success_message('Sent daily digest')
