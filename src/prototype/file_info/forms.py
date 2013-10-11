from __future__ import unicode_literals
from django import forms
from .models import FileInfo

class FileUploadForm(forms.Form):
    uploaded_file = forms.FileField()

class PermChoiceForm(forms.Form):
    NONE = FileInfo.NONE
    NONE_NAME = "Can not Read and Write"
    READ = FileInfo.READ
    READ_NAME = "Can only Read"
    READ_AND_WRITE = FileInfo.READ_AND_WRITE
    READ_AND_WRITE_NAME = "Can Read and Write"

    CHOICE = (
        (NONE, NONE_NAME),
        (READ, READ_NAME),
        (READ_AND_WRITE, READ_AND_WRITE_NAME),
    )
    
    owner_perm = forms.ChoiceField(
                                   choices=CHOICE)
    group_perm = forms.ChoiceField(
                                   choices=CHOICE)
    everyone_perm = forms.ChoiceField(
                                      choices=CHOICE)
