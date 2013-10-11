from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class FileInfo(models.Model):
    file = models.FileField(upload_to='test_upload')
    
    # permission field
    # 0 for none permission
    # 1 for can ONLY read permission
    # 3 for can read & write permission
    owner_perm = models.SmallIntegerField()
    group_perm = models.SmallIntegerField()
    everyone_perm = models.SmallIntegerField()
    
    # relationship
    owner = models.ManyToManyField(User)
    # project_set
