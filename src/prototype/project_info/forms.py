
from django import forms
from project_info.models import ProjectInfo

class ProjectNameHandlerForm(forms.Form):
    error_message = {
            'duplicate': 'Already has a project named {}',      
    }
    
    project_name = forms.CharField(required=True, 
                                   max_length=50, 
                                   min_length=3)
    def clean(self):
        project_name = self.cleaned_data.get('project_name')
        if ProjectInfo.objects.filter(name=project_name):
            # duplicate
            raise forms.ValidationError(
                    message=self.error_message['duplicate'].format(project_name))
        else:
            return self.cleaned_data

class ProjectDescriptionHandlerForm(forms.Form):
    project_description = forms.CharField(required=False,
                                          max_length=5000)


