from celery import Celery

app = Celery("tasks")
app.conf.update(
    enable_utc=False,
    broker_url="redis://redis:6379/0",
    result_backend="redis",
)


@app.task
def add(x, y):
    return x + y
