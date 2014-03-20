from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

from django_extensions.db.fields.json import JSONField

class AkornUserManager(BaseUserManager):
    def create_user(self, email, password=None, settings=None):
        if not email:
            msg = 'Users must have an email address'
            raise ValueError(msg)

        user = self.model(
            email = AkornUserManager.normalize_email(email),
            settings = settings,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, settings=None):
        user = self.create_user(email,
            password=password,
            settings=settings)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class AkornUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True
        )
    # Stores a JSON blob of saved searches etc
    settings = JSONField(blank=True, null=True)

    USERNAME_FIELD = 'email'

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = AkornUserManager()

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email
