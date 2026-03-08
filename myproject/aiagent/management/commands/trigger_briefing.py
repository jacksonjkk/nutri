from django.core.management.base import BaseCommand
from aiagent.tasks import send_morning_briefing_task

class Command(BaseCommand):
    help = 'Manually trigger the morning briefing agent'

    def handle(self, *args, **options):
        self.stdout.write('Starting Morning Briefing Agent...')
        result = send_morning_briefing_task()
        self.stdout.write(self.style.SUCCESS(f'Successfully completed: {result}'))
