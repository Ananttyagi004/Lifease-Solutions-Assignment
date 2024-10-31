
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cricket_scraper.settings')

# Initialize Celery
app = Celery('cricket_scraper')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in the Django project
app.autodiscover_tasks()
