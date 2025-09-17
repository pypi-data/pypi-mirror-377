from celery import Celery
import os

# Get Celery configuration from environment variables
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize the Celery application
celery_app = Celery("oak", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

# This will automatically discover tasks in the `tasks` directory
celery_app.autodiscover_tasks(['oak.tasks.library'], related_name='tasks')