import os

from celery import Celery

# Set the default Django settings module before importing anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BI_Project.settings')

# Create Celery app instance
app = Celery('BI_Project')

# Load configuration from Django settings with namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from installed apps
app.autodiscover_tasks(['Sales'])


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery works"""
    print(f'Request: {self.request!r}')


if __name__ == '__main__':
    app.start()
