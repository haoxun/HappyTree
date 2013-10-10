from django import forms

class FileUploadForm(forms.Form):
    uploaded_file = forms.FileField()

