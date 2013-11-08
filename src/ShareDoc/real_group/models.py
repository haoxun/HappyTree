from __future__ import unicode_literals
from django.db import models
from guardian.models import Group
from user_info.models import UserInfo
# Create your models here.


class RealGroup(models.Model):
    # field
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relationship
    group = models.OneToOneField(Group)
    user_infos_ac = models.ManyToManyField(UserInfo,
                                           through='UserInfo_RealGroup_AC')
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


class BasicAC(object):
    STATUS_WAIT = 'WAIT'
    STATUS_ACCEPT = 'ACCEPT'
    STATUS_DENY = 'DENY'
    STATUS_FINISH = 'FINISH'


class UserInfo_RealGroup_AC(models.Model, BasicAC):
    ACTION_UTR = 'UTR'
    ACTION_RTU = 'RTU'

    # relations
    user_info = models.ForeignKey(UserInfo,
                                  related_name="real_groups_ac")
    # class defined in RealGroup, no related_name needed.
    real_group = models.ForeignKey(RealGroup)

    # extra files
    created_time = models.DateTimeField(auto_now_add=True)
    # Action: "UserInfoToRealGroup"(UTR), "RealGroupToUserInfo"(RTU)
    action_code = models.CharField(max_length=3)
    # Status: "ACCEPT", "DENY", "WAIT"
    action_status = models.CharField(max_length=6)

    class Meta:
        # can be hold by users.
        permissions = (
            ('process_user_real_group_ac', 'can process the accept/confirm'),
        )

    def __unicode__(self):
        return '{}'.format(unicode(self.id))
