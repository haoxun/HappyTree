from django.db import models

from file_info.models import FileInfo
from group_info.models import GroupInfo

# Create your models here.
class ProjectInfo(models.Model):
    # fields
    name = models.CharField(max_length=250, unique=True)
    project_description = models.CharField(max_length=250)
    # relationship
    normal_group = models.ManyToManyField(GroupInfo, 
                                          related_name='normal_in_project')
    super_group = models.ManyToManyField(GroupInfo, 
                                          related_name='super_in_project')

    def __unicode__(self):
        return u'{}'.format(self.name)

class Message(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    # relation
    project_info = models.ForeignKey(ProjectInfo)
    file_info = models.ManyToManyField(FileInfo)
    
    def __unicode__(self):
        return u'{}'.format(self.id)


