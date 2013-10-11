from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UniqueFile(models.Model):
    file = models.FileField(upload_to='test_upload')
    md5 = models.CharField(max_length=32)

    def __unicode__(self):
        return '{}'.format(self.id)

class FileInfo(models.Model):
    NONE = 'N'
    READ = 'R'
    READ_AND_WRITE = 'R&W'
    
    file_name = models.CharField(max_length=200)
    
    # permission field
    # NONE for none permission
    # READ for can ONLY read permission
    # READ_AND_WRITE for can read & write permission
    owner_perm = models.CharField(max_length=3)
    group_perm = models.CharField(max_length=3)
    everyone_perm = models.CharField(max_length=3)
    
    # relationship
    owner = models.ManyToManyField(User)
    unique_file = models.ForeignKey(UniqueFile)
    # project_set

    def __unicode__(self):
        return '{}'.format(self.id)


