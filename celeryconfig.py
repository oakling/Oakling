from datetime import timedelta

BROKER_URL = "amqplib://akorn:akorn@ip-10-235-51-20:5672/myvhost"

BROKER_HOST = "ip-10-235-51-20"

BROKER_PORT = 49724
BROKER_USER = "akorn"
BROKER_PASSWORD = "flout29&UFOs"

BROKER_VHOST = "myvhost"

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = (
    "lib.scrapers.journals.tasks",
    "lib.scrapers.feeds.tasks",
)

CELERY_ENABLE_UTN = True
CELERY_TIMEZONE = "Europe/London"

CELERYBEAT_SCHEDULE = {
    "APS_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_APS_feeds",
        "schedule": timedelta(hours=1),
    },
}
