import os
from celery import Celery


app = Celery("tasks")
app.conf.update(
    enable_utc=False,
    timezone=os.getenv("TZ"),
    broker_url=os.getenv("CELERY_REDIS_URL"),
    result_backend=os.getenv("CELERY_REDIS_URL"),

    beat_schedule={
        "hello-every-1-minute": {
            "task": "investment_local_horse_racing_trader.celery.tasks.hello",
            "schedule": 60.0,
        }
    }
)


@app.task
def add(x, y):
    return x + y


@app.task
def hello():
    return "hello"
