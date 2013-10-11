from __future__ import unicode_literals
from django import forms
from .models import FileInfo

class FileUploadForm(forms.Form):
    uploaded_file = forms.FileField()

    def clean(self):
        if 'file_upload_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data
            

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
    def clean(self):
        if 'file_upload_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data


class MessageInfoForm(forms.Form):
    title = forms.CharField(required=False,
                            max_length=50)
    description = forms.CharField(required=False,
                                  max_length=500)
    def clean(self):
        if 'post_message_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data

