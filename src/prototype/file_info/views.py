# Create your views here.

# remember, always include project info id.
from .forms import FileUploadForm
from django.shortcuts import render
def create_message(request, project_info_id):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print request.FILES['uploaded_file'].read()
            return render(request,
                          'file_info/create_message_page.html',
                          {
                              'project_info_id': int(project_info_id),
                              'form': form
                              })
    else:
        form = FileUploadForm()
    return render(request,
                  'file_info/create_message_page.html',
                  {
                    'project_info_id': int(project_info_id),
                    'form': form
                    })


