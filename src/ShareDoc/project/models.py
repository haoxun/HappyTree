from __future__ import unicode_literals
from django.db import models
from user_info.models import UserInfo
from real_group.models import RealGroup
from guardian.models import Group

# Create your models here.
class Project(models.Model):
    # fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relations
    # real groups attended to project
    real_groups = models.ManyToManyField(RealGroup,
                                         related_name='attended_projects')
    # users not exsiting in any attended real group
    users_without_groups = models.ManyToManyField(UserInfo,
                                                  related_name='attended_projects_without_group')
    # apply/confirm relations
    users_ac = models.ManyToManyField(UserInfo, 
                                      through="UserInfo_Project_AC")
    real_groups_ac = models.ManyToManyField(RealGroup,
                                            through="RealGroup_Project_AC")

    # ForeignKey
    # project_groups: project groups to hold all attended users and permission management.
    # messages: messages related to the project.
    
    class Meta:
        # can be hold by user
        permissions = (
                ('membership', 'member of the project'),
                ('ownership', 'owner of the project'),
                ('management', 'manager of the project'),
                
        )

    def __unicode__(self):
        return '{}'.format(self.name)

class ProjectGroup(models.Model):
    # fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # permissions
    download = models.BooleanField()
    upload = models.BooleanField()
    delete = models.BooleanField()
    # relations
    # hold users
    group = models.OneToOneField(Group)
    # related to a project
    project = models.ForeignKey(Project,
                                related_name='project_groups')
    class Meta:
        # can be hold by project group
        permissions = (
                ('membership', 'member of the project group'),
                ('download', 'can download file'),
                ('delete', 'can delete file'),
                ('upload', 'can upload file')

        ) 

# with consideration of circuit import problem,
# apply/confirm relaions related to UserInfo and RealGroup, both
# "connected" to Project, are defined in this file.
class UserInfo_Project_AC(models.Model):
    # relations
    user_info = models.ForeignKey(UserInfo, 
                                  related_name="projects_ac")
    # class defined in Project, no related_name needed.
    project = models.ForeignKey(Project)
    
    # extra files
    # Action: "UserInfoToProject", "ProjectToUserInfo"
    action_code = models.CharField(max_length=17)
    # Status: "ACCEPT", "DENY", "WAIT"
    action_status = models.CharField(max_length=6)
    
class RealGroup_Project_AC(models.Model):
    # relations
    real_group = models.ForeignKey(RealGroup, 
                                   related_name="projects_ac")
    # class defined in Project, no related_name needed.
    project = models.ForeignKey(Project)
    
    # extra files
    # Action: "UserInfoToProject", "ProjectToUserInfo"
    action_code = models.CharField(max_length=17)
    # Status: "ACCEPT", "DENY", "WAIT"
    action_status = models.CharField(max_length=6)


    

class Message(models.Model):
    # fields
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now=True)
    post_flag = models.BooleanField(default=False)
    # relation
    project = models.ForeignKey(Project,
                                related_name='messages')
    # ForeignKey
    # file_pointers: pointers to files be in the message

    class Meta:
        # can be held by poster
        permissions = (
                ('ownership', 'owner of the message'),
                
        )
    
    def __unicode__(self):
        return '{}'.format(self.id)
