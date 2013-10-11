# Create your views here.

# remember, always include project info id.

from .forms import FileUploadForm
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from project_info.models import ProjectInfo, Message
from file_info.models import FileInfo


@login_required
def create_message(request, project_info_id, message_id):
    project_info_id = int(project_info_id)
    project_info = get_object_or_404(ProjectInfo, id=project_info_id)
    if message_id == None:
        # create_message
        message = Message(project_info=project_info)
        message.save()
        return redirect('create_message_page',
                        project_info_id=project_info_id,
                        message_id=message.id)
    else:
        message_id = int(message_id)
        message = get_object_or_404(Message, 
                                    project_info=project_info,
                                    id=message_id)
    # process form
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['uploaded_file']
            file_info = FileInfo(owner_perm=3,
                                 group_perm=3,
                                 everyone_perm=3)
            file_info.file.save(uploaded_file.name, uploaded_file)
            file_info.owner.add(request.user)
            message.file_info.add(file_info)

            return render(request,
                          'file_info/create_message_page.html',
                          {
                              'project_info_id': int(project_info_id),
                              'form': form,
                              'message_id': message.id,
                              })
    else:
        form = FileUploadForm()
    return render(request,
                  'file_info/create_message_page.html',
                  {
                    'project_info_id': int(project_info_id),
                    'form': form,
                    'message_id': message.id,
                    })


