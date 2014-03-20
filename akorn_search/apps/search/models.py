from django.db import models

from django_extensions.db.fields.json import JSONField

from apps.accounts.models import AkornUser

class Search(models.Model):
    query = JSONField()
    last_visited = models.DateTimeField()
    user = models.ForeignKey(AkornUser, blank=True, null=True)
