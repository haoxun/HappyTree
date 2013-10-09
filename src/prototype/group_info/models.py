from django.db import models
from django.contrib.auth.models import Group, User

# Create your models here.
class GroupInfo(models.Model):
    # field
    group_description = models.CharField(max_length=250)
                                         
    # There are two types of group, 
    # one for real world relationship among users, 
    # one for authorization management of projects.
    # real_group represents a real world relationship if its value is True.
    real_group = models.BooleanField(default=True)
    
    # relationship
    group = models.OneToOneField(Group)
    manager_user = models.ManyToManyField(User)
    # normal_in_project
    # super_in_project

    def __unicode__(self):
        return u'{}'.format(self.group.name)
