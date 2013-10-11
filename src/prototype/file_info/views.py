# Create your views here.

# remember, always include project info id.

from .forms import FileUploadForm, PermChoiceForm
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
    # generate uploaded file list

    # process form
    if request.method == 'POST':
        file_upload_form = FileUploadForm(request.POST, request.FILES)
        perm_choice_form = PermChoiceForm(request.POST)

        if file_upload_form.is_valid() and perm_choice_form.is_valid():
            uploaded_file = request.FILES['uploaded_file']
            owner_perm = perm_choice_form.cleaned_data['owner_perm']
            group_perm = perm_choice_form.cleaned_data['group_perm']
            everyone_perm = perm_choice_form.cleaned_data['everyone_perm']

            file_info = FileInfo(owner_perm=owner_perm,
                                 group_perm=group_perm,
                                 everyone_perm=everyone_perm)
            file_info.file.save(uploaded_file.name, uploaded_file)
            file_info.owner.add(request.user)
            message.file_info.add(file_info)
        return redirect('create_message_page',
                        project_info_id=project_info_id,
                        message_id=message.id)
    else:
        file_upload_form = FileUploadForm()
        perm_choice_form = PermChoiceForm(initial={
                    'owner_perm': FileInfo.READ_AND_WRITE, 
                    'everyone_perm': FileInfo.READ, 
                    'group_perm': FileInfo.READ
                    })

    # rendering
    render_data_dict = {
            'project_info_id': int(project_info_id),
            'file_upload_form': file_upload_form,
            'perm_choice_form': perm_choice_form,
            'message_id': message.id,
    }
    return render(request,
                  'file_info/create_message_page.html',
                  render_data_dict)


