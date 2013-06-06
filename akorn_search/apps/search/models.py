from django.contrib.auth.models import AbstractBaseUser

from django_extensions.db.fields.json import JSONField

class AkornUser(AbstractBaseUser):
    # Stores a JSON blob of saved searches etc
    settings_doc = JSONField(blank=True, null=True)
