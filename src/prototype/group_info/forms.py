
from django import forms
from django.contrib.auth.models import Group, User

class GroupNameHandlerForm(forms.Form):
    error_message = {
            'duplicate': 'Already has a group named {}',      
    }
    
    group_name = forms.CharField(required=True, 
                                 max_length=50, 
                                 min_length=3)
    def clean(self):
        group_name = self.cleaned_data.get('group_name')
        try:
            Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return self.cleaned_data
        else:
            raise forms.ValidationError(
                    message=self.error_message['duplicate'].format(group_name))

class GroupDescriptionHandlerForm(forms.Form):
    group_description = forms.CharField(required=False,
                                        max_length=5000)


class AddUserForm(forms.Form):
    error_message = {
            'empty': 'Not exist user named {}',
    }

    username = forms.CharField(required=True)
    
    def clean(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                    message=self.error_message['empty'].format(username))
        else:
            return self.cleaned_data
    

