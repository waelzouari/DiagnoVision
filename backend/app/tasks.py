from .celery_app import celery_app


@celery_app.task(name="app.tasks.scheduled_analysis")
def scheduled_analysis() -> dict:
    # The API service owns authorization and immutable analysis creation. The beat task
    # provides a safe integration seam; deployment can enqueue per-doctor work here.
    return {"status": "scan_completed"}

