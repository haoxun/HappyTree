from __future__ import unicode_literals
from django.db import models
from project.models import Message
# Create your models here.


class UniqueFile(models.Model):
    file = models.FileField(upload_to='test_upload')
    md5 = models.CharField(max_length=32)

    # ForeignKey
    # file_pointers

    def __unicode__(self):
        return '{}'.format(self.id)


class FilePointer(models.Model):
    # field
    name = models.CharField(max_length=50)

    # relationship
    message = models.ForeignKey(Message,
                                related_name='file_pointers')
    unique_file = models.ForeignKey(UniqueFile,
                                    related_name='file_pointers')

    def __unicode__(self):
        return '{}'.format(self.id)
