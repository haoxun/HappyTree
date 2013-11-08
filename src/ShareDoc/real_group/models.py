from __future__ import unicode_literals
from django.db import models
from guardian.models import Group
from user_info.models import UserInfo


class RealGroup(models.Model):
    # field
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relationship
    group = models.OneToOneField(Group)
    user_infos_ac = models.ManyToManyField(UserInfo,
                                           through='notification.UserInfo_RealGroup_AC')
    # ManyToManyField
    # projects_ac: apply/confirm relations to project.
    # ForeignKey
    # attended_projects: self explanation.

    class Meta:
        # can be hold by group's users.
        permissions = (
            ('real_group_ownership', 'owner of the group'),
            ('real_group_membership', 'member of the group'),
            ('real_group_management', 'manager of the group'),
        )

    def __unicode__(self):
        return '[{0}][{1}]'.format(unicode(self.id), self.name)
