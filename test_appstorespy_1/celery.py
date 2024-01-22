import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_appstorespy_1.settings")
app = Celery("test_appstorespy_1")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
