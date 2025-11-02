"""
Celery application configuration
"""
from celery import Celery
from backend.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "ai_scheduler",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['backend.workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # Soft limit at 25 minutes
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_max_tasks_per_child=50,  # Restart worker after 50 tasks
)

if __name__ == '__main__':
    celery_app.start()
