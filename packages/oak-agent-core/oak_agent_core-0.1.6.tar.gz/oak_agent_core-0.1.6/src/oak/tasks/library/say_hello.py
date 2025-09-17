from oak.celery_app import celery_app

@celery_app.task(name="say_hello_task")
def say_hello_task(message):
    """
    A simple task to demonstrate Celery functionality.
    """
    print(f"Hello from Celery worker! Message: {message}")
    return "Task completed."