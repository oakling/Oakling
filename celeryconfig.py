from celery.schedules import crontab

BROKER_URL = "amqplib://akorn:akorn@127.0.0.1/myvhost" #amqplib://akorn:akorn@ip-10-235-51-20:5672/myvhost"

#BROKER_HOST = "PopeBook-Pro" #ip-10-235-51-20"
#BROKER_PORT = 49724
#BROKER_USER = "akorn"
#BROKER_PASSWORD = "flout29&UFOs"
#BROKER_VHOST = "myvhost"

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = (
    "lib.scrapers.journals.tasks",
    "lib.scrapers.feeds.tasks",
)

CELERY_ENABLE_UTN = True
CELERY_TIMEZONE = "Europe/London"

CELERYBEAT_SCHEDULE = {
    "APS_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=0, hour="*"),
        "args":("aps_feed",
                ["http://feeds.aps.org/rss/recent/prl.xml",
                 "http://feeds.aps.org/rss/recent/pra.xml",
                 "http://feeds.aps.org/rss/recent/prb.xml",
                 "http://feeds.aps.org/rss/recent/prc.xml",
                 "http://feeds.aps.org/rss/recent/prd.xml",
                 "http://feeds.aps.org/rss/recent/pre.xml",
                 "http://feeds.aps.org/rss/recent/prx.xml",
                ],
               )
    },
}
