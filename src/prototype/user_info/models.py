from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserInfo(models.Model):
    # field
    email = models.CharField(max_length=50)

    # relationship
    user = models.OneToOneField(User)

    def __unicode__(self):
        return '{}'.format(self.user)
