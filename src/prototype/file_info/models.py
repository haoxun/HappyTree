from django.db import models
from user_status.models import UserInfo
# Create your models here.

class FileInfo(models.Model):
    file = models.FileField(upload_to='%Y/%m/%d')
    
    # permission field
    # 0 for none permission
    # 1 for can ONLY read permission
    # 3 for can read & write permission
    owner_perm = models.SmallIntegerField()
    group_perm = models.SmallIntegerField()
    everyone_perm = models.SmallIntegerField()
    
    # relationship
    owner = models.OneToOneField(UserInfo)
    # project_set
