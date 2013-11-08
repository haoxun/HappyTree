from __future__ import unicode_literals
from django.db import models
from user_info.models import UserInfo
from real_group.models import RealGroup
from guardian.models import Group


class ProjectGroup(models.Model):
    # fields
    # default permissions
    download = models.BooleanField()
    upload = models.BooleanField()
    delete = models.BooleanField()
    # relations
    # held users
    group = models.OneToOneField(Group)

    def __unicode__(self):
        return '{}'.format(self.id)


class Project(models.Model):
    # fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relations
    # real groups attended to project
    real_groups = models.ManyToManyField(RealGroup,
                                         related_name='attended_projects')
    # hold all members of the project.
    project_group = models.OneToOneField(ProjectGroup)
    # apply/confirm relations
    user_infos_ac = models.ManyToManyField(UserInfo,
                                           through="notification.UserInfo_Project_AC")
    real_groups_ac = models.ManyToManyField(RealGroup,
                                            through="notification.RealGroup_Project_AC")
    # ForeignKey
    # project_groups: project groups
    # to hold all attended users and permission management.
    # messages: messages related to the project.

    class Meta:
        # can be hold by user
        permissions = (
            ('project_ownership', 'owner of the project'),
            ('project_membership', 'member of the project'),
            ('project_management', 'manager of the project'),
            ('project_download', 'can download file'),
            ('project_delete', 'can delete file'),
            ('project_upload', 'can upload file')
        )

    def __unicode__(self):
        return '{}'.format(self.name)
