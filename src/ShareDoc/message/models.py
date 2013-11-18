from __future__ import unicode_literals
from django.db import models
from project.models import Project
from user_info.models import UserInfo


class Message(models.Model):
    # fields
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    post_time = models.DateTimeField(auto_now=True)
    post_flag = models.BooleanField(default=False)
    # relation
    project = models.ForeignKey(Project,
                                related_name='messages')
    owner = models.ForeignKey(UserInfo,
                              related_name="messages")
    # ForeignKey
    # file_pointers: pointers to files be in the message

    def __unicode__(self):
        return '{}'.format(self.id)


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
