from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "creatorpulse",
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery_app.task
def run_daily_digest(user_id: str):
    print(f"Running digest for user {user_id}")
    # Step 5 will fill this in
    return {"status": "pending", "user_id": user_id}