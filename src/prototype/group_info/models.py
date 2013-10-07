from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class GroupInfo(models.Model):
    # relationship
    group = models.OneToOneField(Group)
    # normal_in_project
    # super_in_project
