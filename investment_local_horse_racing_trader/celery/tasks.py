import os
from celery import Celery
from celery_slack import Slackify

from investment_local_horse_racing_trader.scrapy.health import health
from investment_local_horse_racing_trader.scrapy.vote import vote


app = Celery("tasks")
app.conf.update(
    enable_utc=False,
    timezone=os.getenv("TZ"),
    broker_url=os.getenv("CELERY_REDIS_URL"),
    result_backend=os.getenv("CELERY_REDIS_URL"),
    worker_concurrency=1,

    # beat_schedule={
    #     "hello-every-1-minute": {
    #         "task": "investment_local_horse_racing_trader.celery.tasks.hello",
    #         "schedule": 60.0,
    #     }
    # }
)


if os.getenv("SLACK_WEBHOOK"):
    slack_app = Slackify(app, os.getenv("SLACK_WEBHOOK"))


@app.task
def web_health():
    return health()


@app.task
def web_vote(race_id, vote_id):
    return vote(race_id, vote_id)
