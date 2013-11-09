from __future__ import unicode_literals
from django.db import models
from guardian.models import User


class UserInfo(models.Model):
    # field
    name = models.CharField(max_length=50)
    email = models.CharField(unique=True,
                             max_length=50)

    # relationship
    user = models.OneToOneField(User)
    # ManyToManyField
    # projects_ac: apply/confirm relations to project
    # real_groups_ac: self explanation.

    def __unicode__(self):
        return '{}'.format(self.user.username)
