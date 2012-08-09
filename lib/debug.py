import couchdb
import celery
import datetime

@celery.task
def rabbit_beat():
  f = open('beat.dat', 'w+')
  print >>f, datetime.datetime.now()

