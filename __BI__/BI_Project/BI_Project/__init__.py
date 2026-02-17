# This will be imported when celery -A config is run


from .Celery import app as celery_app

__all__ = ('celery_app',)