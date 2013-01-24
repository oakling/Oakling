from django.db import models

class Pane(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=255)

    def __unicode__(self):
            return u'%s' % self.name
