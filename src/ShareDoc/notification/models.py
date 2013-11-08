from __future__ import unicode_literals
from django.db import models
from user_info.models import UserInfo
from real_group.models import RealGroup
from project.models import Project


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


# with consideration of circuit import problem,
# apply/confirm relaions related to UserInfo and RealGroup, both
# "connected" to Project, are defined in this file.
# ATB == A apply To B
class UserInfo_Project_AC(models.Model, BasicAC):
    ACTION_UTP = 'UTP'
    ACTION_PTU = 'PTU'
    # relations
    user_info = models.ForeignKey(UserInfo,
                                  related_name="projects_ac")
    # class defined in Project, no related_name needed.
    project = models.ForeignKey(Project)

    # extra files
    created_time = models.DateTimeField(auto_now_add=True)
    # Action: "UserInfoToProject"(UTP), "ProjectToUserInfo"(PTU)
    action_code = models.CharField(max_length=3)
    # Status: "ACCEPT", "DENY", "WAIT"
    action_status = models.CharField(max_length=6)

    class Meta:
        # can be hold by users.
        permissions = (
            ('process_user_project_ac', 'can process the accept/confirm'),
        )

    def __unicode__(self):
        return '{}'.format(self.id)


class RealGroup_Project_AC(models.Model, BasicAC):
    ACTION_RTP = 'RTP'
    ACTION_PTR = 'PTR'
    # relations
    real_group = models.ForeignKey(RealGroup,
                                   related_name="projects_ac")
    # class defined in Project, no related_name needed.
    project = models.ForeignKey(Project)

    # extra files
    created_time = models.DateTimeField(auto_now_add=True)
    # Action: "RealGroupToProject"(RTP), "ProjectToRealGroup"(PTR)
    action_code = models.CharField(max_length=3)
    # Status: "ACCEPT", "DENY", "WAIT"
    action_status = models.CharField(max_length=6)

    class Meta:
        # can be hold by users.
        permissions = (
            ('process_real_group_project_ac', 'can process the accept/confirm'),
        )

    def __unicode__(self):
        return '{}'.format(self.id)
