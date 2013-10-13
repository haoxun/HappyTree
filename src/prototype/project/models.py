from __future__ import unicode_literals
from django.db import models

from django.contrib.auth.models import User, Group
from group_info.models import GroupInfo

# Create your models here.
class Project(models.Model):
    # fields
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relationship
    owner = models.OneToOneField(User)
    # groups for permission control and the isolation of real groups
    manage_group = models.OneToOneField(Group, 
                                        related_name='manage_in_project')
    normal_group = models.ForeignKey(Group, 
                                     related_name='normal_in_project')
    # real groups attended to project
    attended_group = models.ManyToManyField(Group, 
                                            related_name='attended_project')

    def __unicode__(self):
        return '{}'.format(self.name)

class Message(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now=True)
    post_flag = models.BooleanField(default=False)
    # relation
    owner = models.OneToOneField(User)
    project = models.ForeignKey(Project)
    
    def __unicode__(self):
        return '{}'.format(self.id)


