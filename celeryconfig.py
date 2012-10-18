from celery.schedules import crontab

BROKER_URL = "amqplib://akorn:akorn@127.0.0.1/myvhost" #amqplib://akorn:akorn@ip-10-235-51-20:5672/myvhost"

#BROKER_HOST = "PopeBook-Pro" #ip-10-235-51-20"
#BROKER_PORT = 49724
#BROKER_USER = "akorn"
#BROKER_PASSWORD = "flout29&UFOs"
#BROKER_VHOST = "myvhost"

CELERY_RESULT_BACKEND = "amqp"

#BROKER_URL = "couchdb://127.0.0.1:5984/celery"
#CELERY_RESULT_BACKEND = 'couchdb'

CELERY_IMPORTS = (
    "lib.scrapers.journals.tasks",
    "lib.scrapers.feeds.tasks",
    "lib.debug",
)

CELERY_ENABLE_UTN = True
CELERY_TIMEZONE = "Europe/London"

CELERYBEAT_SCHEDULE = {
    "debug": {
       "task": "lib.debug.rabbit_beat",
       "schedule": crontab(minute="*/15"),
    },
    "APS_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=1, hour="15"),
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
    "ACS_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=1, hour="15"),
        "args":("acs_feed",
                ["http://feeds.feedburner.com/acs/jacsat"],
               )
    },
    "IOP_feeds":{
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=5, hour="12"),
        "args":("iop_feed",
                [
                    "http://iopscience.iop.org/1538-3881/?rss=1",
                    "http://iopscience.iop.org/1538-4357/?rss=1",
                    "http://iopscience.iop.org/0067-0049/?rss=1",
                    "http://iopscience.iop.org/1748-3190/?rss=1",
                    "http://iopscience.iop.org/1748-605X/?rss=1",
                    "http://iopscience.iop.org/1009-9271/?rss=1",
                    "http://iopscience.iop.org/1674-0068/?rss=1",
                    "http://iopscience.iop.org/1674-1056/?rss=1",
                    "http://iopscience.iop.org/0256-307X/?rss=1",
                    "http://iopscience.iop.org/0264-9381/?rss=1",
                    "http://iopscience.iop.org/0295-5075/?rss=1",
                    "http://iopscience.iop.org/1748-9326/?rss=1",
                    "http://iopscience.iop.org/0143-0807/?rss=1",
                    "http://iopscience.iop.org/0266-5611/?rss=1",
                    "http://iopscience.iop.org/1752-7163/?rss=1",
                    "http://iopscience.iop.org/1475-7516/?rss=1",
                    "http://iopscience.iop.org/1742-2140/?rss=1",
                    "http://iopscience.iop.org/1126-6708/?rss=1",
                    "http://iopscience.iop.org/1748-0221/?rss=1",
                    "http://iopscience.iop.org/0960-1317/?rss=1",
                    "http://iopscience.iop.org/1741-2552/?rss=1",
                    "http://iopscience.iop.org/1464-4258/?rss=1",
                    "http://iopscience.iop.org/0305-4470/?rss=1",
                    "http://iopscience.iop.org/1751-8121/?rss=1",
                    "http://iopscience.iop.org/0953-4075/?rss=1",
                    "http://iopscience.iop.org/0022-3727/?rss=1",
                    "http://iopscience.iop.org/0954-3899/?rss=1",
                    "http://iopscience.iop.org/0953-8984/?rss=1",
                    "http://iopscience.iop.org/1742-6596/?rss=1",
                    "http://iopscience.iop.org/0952-4746/?rss=1",
                    "http://iopscience.iop.org/1742-5468/?rss=1",
                    "http://iopscience.iop.org/0957-0233/?rss=1",
                    "http://iopscience.iop.org/0026-1394/?rss=1",
                    "http://iopscience.iop.org/0965-0393/?rss=1",
                    "http://iopscience.iop.org/0957-4484/?rss=1",
                    "http://iopscience.iop.org/1367-2630/?rss=1",
                    "http://iopscience.iop.org/0951-7715/?rss=1",
                    "http://iopscience.iop.org/0029-5515/?rss=1",
                    "http://iopscience.iop.org/1402-4896/?rss=1",
                    "http://iopscience.iop.org/1478-3975/?rss=1",
                    "http://iopscience.iop.org/0031-9120/?rss=1",
                    "http://iopscience.iop.org/0031-9155/?rss=1",
                    "http://iopscience.iop.org/0967-3334/?rss=1",
                    "http://iopscience.iop.org/0741-3335/?rss=1",
                    "http://iopscience.iop.org/1009-0630/?rss=1",
                    "http://iopscience.iop.org/0963-0252/?rss=1",
                    "http://iopscience.iop.org/0034-4885/?rss=1",
                    "http://iopscience.iop.org/0268-1242/?rss=1",
                    "http://iopscience.iop.org/0964-1726/?rss=1",
                    "http://iopscience.iop.org/0953-2048/?rss=1",
                    "http://iopscience.iop.org/0004-637X/?rss=1",
                ],
        )
    },
    "arxiv_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=10, hour="0"),
        "args":("arxiv_feed",
                ['http://export.arxiv.org/rss/astro-ph',
                 'http://export.arxiv.org/rss/cond-mat',
                 'http://export.arxiv.org/rss/cs',
                 'http://export.arxiv.org/rss/gr-qc',
                 'http://export.arxiv.org/rss/hep-ex',
                 'http://export.arxiv.org/rss/hep-lat',
                 'http://export.arxiv.org/rss/hep-ph',
                 'http://export.arxiv.org/rss/hep-th',
                 'http://export.arxiv.org/rss/math',
                 'http://export.arxiv.org/rss/math-ph',
                 'http://export.arxiv.org/rss/nlin',
                 'http://export.arxiv.org/rss/nucl-ex',
                 'http://export.arxiv.org/rss/nucl-th',
                 'http://export.arxiv.org/rss/physics',
                 'http://export.arxiv.org/rss/q-bio',
                 'http://export.arxiv.org/rss/q-fin',
                 'http://export.arxiv.org/rss/quant-ph',
                 'http://export.arxiv.org/rss/stat',
                ],
               )
    },
    "Nature_feeds": {
        "task": "lib.scrapers.feeds.tasks.fetch_feed",
        "schedule": crontab(minute=1, hour="*"),
        "args":("nature_feed",
                ["http://feeds.nature.com/NatureLatestResearch"],
               )
    },
}
