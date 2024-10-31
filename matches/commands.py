from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule

class Command(BaseCommand):
    help = 'Sets up periodic tasks for the cricket scraper'

    def handle(self, *args, **kwargs):
        # Create or get the crontab schedule (every 6 hours)
        schedule, created = CrontabSchedule.objects.get_or_create(
            hour='*/6', minute=0
        )

        # Create the periodic task for scraping match list
        PeriodicTask.objects.get_or_create(
            crontab=schedule,
            name='Scrape Match List',
            task='matches.tasks.scrape_match_list'
        )

        self.stdout.write(self.style.SUCCESS('Periodic task setup complete.'))