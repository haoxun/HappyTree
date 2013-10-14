from __future__ import unicode_literals
from django.db import models
from guardian.models import Group, User
# Create your models here.
class RealGroup(models.Model):
    # field
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    
    # relationship
    group = models.OneToOneField(Group)
    # ManyToManyField
    # projects_ac: apply/confirm relations to project.
    # ForeignKey
    # attended_projects: self explanation.
    

    class Meta:
        # can be hold by group's users.
        permissions = (
                ('ownership', 'owner of the group'),
                ('membership', 'member of the group'),
                ('management', 'manager of the group'),

        )


    def __unicode__(self):
        return '{}'.format(self.group)
