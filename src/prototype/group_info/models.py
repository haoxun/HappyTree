from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import Group, User
# Create your models here.
class GroupInfo(models.Model):
    # field
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
                                         
    # There are two types of group, 
    # one for real world relationship among users, 
    # one for authorization management of projects.
    # real_flag represents a real world relationship if its value is True.
    real_flag = models.BooleanField(default=True)
    
    # relationship
    group = models.OneToOneField(Group)
    manager = models.ManyToManyField(User, related_name='manage_in_group')
    owner = models.ForeignKey(User, related_name='owned_group')


    def __unicode__(self):
        return '{}'.format(self.group)
