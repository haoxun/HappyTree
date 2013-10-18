from __future__ import unicode_literals
from django import forms
from file_storage.models import FilePointer

class FileUploadForm(forms.Form):
    uploaded_file = forms.FileField()

    def clean(self):
        if 'file_upload_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data
            

class ProjectChoiceForm(forms.Form):
    def __init__(self, project_set, *args, **kwagrs):
        super(ProjectChoiceForm, self).__init__(*args, **kwagrs)
        project_candidates = [(project.id, project.name) \
                                    for project in project_set]
        self.fields['project_id'] = forms.ChoiceField(choices=project_candidates)
    def clean(self):
        if 'post_message_submit' not in self.data:
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

