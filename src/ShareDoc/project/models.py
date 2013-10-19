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
                                           through="UserInfo_Project_AC")
    real_groups_ac = models.ManyToManyField(RealGroup,
                                            through="RealGroup_Project_AC")

    # ForeignKey
    # project_groups: project groups to hold all attended users and permission management.
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



# with consideration of circuit import problem,
# apply/confirm relaions related to UserInfo and RealGroup, both
# "connected" to Project, are defined in this file.
# ATB == A apply To B
class UserInfo_Project_AC(models.Model):
    ACTION_UTP = 'UTP'
    ACTION_PTU = 'PTU'
    STATUS_WAIT = 'WAIT'
    STATUS_ACCEPT = 'ACCEPT'
    STATUS_DENY = 'DENY'
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
    
class RealGroup_Project_AC(models.Model):
    ACTION_RTP = 'RTP'
    ACTION_PTR = 'PTR'
    STATUS_WAIT = 'WAIT'
    STATUS_ACCEPT = 'ACCEPT'
    STATUS_DENY = 'DENY'
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


    

class Message(models.Model):
    # fields
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now=True)
    post_flag = models.BooleanField(default=False)
    # relation
    project = models.ForeignKey(Project,
                                related_name='messages')
    owner = models.ForeignKey(UserInfo,
                              related_name="messages")
    # ForeignKey
    # file_pointers: pointers to files be in the message

    class Meta:
        # can be held by poster
        permissions = (
                ('message_processing', 'owner of the message has not being post'),
                
        )
    
    def __unicode__(self):
        return '{}'.format(self.id)
