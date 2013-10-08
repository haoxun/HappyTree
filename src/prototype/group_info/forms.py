
from django import forms
from django.contrib.auth.models import Group

class CreateGroupForm(forms.Form):
    error_message = {
            'duplicate': "Already has a group named {}",      
    }
    
    group_name = forms.CharField(required=True, 
                                 max_length=50, 
                                 min_length=3)
    group_description = forms.CharField(required=False)
    
    def clean(self):
        group_name = self.cleaned_data.get('group_name')
        try:
            Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return self.cleaned_data
        else:
            raise forms.ValidationError(message= \
                    self.error_message['duplicate'].format(group_name))


