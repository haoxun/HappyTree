from __future__ import unicode_literals
from django import forms
from message.models import FilePointer


class FileUploadForm(forms.Form):
    uploaded_file = forms.FileField()


class ProjectChoiceForm(forms.Form):
    def __init__(self, project_set, *args, **kwagrs):
        super(ProjectChoiceForm, self).__init__(*args, **kwagrs)
        project_candidates = []
        for project in project_set:
            project_candidates.append(
                (project.id, project.name),
            )
        self.fields['project_id'] = forms.ChoiceField(
            choices=project_candidates,
        )

    def clean(self):
        if 'post_message_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data


class MessageInfoForm(forms.Form):
    title = forms.CharField(required=False,
                            max_length=50)
    description = forms.CharField(required=False,
                                  max_length=500,
                                  widget=forms.Textarea)

    def clean(self):
        if 'post_message_submit' not in self.data:
            raise forms.ValidationError("Not Being Submit")
        return self.cleaned_data
