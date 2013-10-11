from __future__ import unicode_literals
# Create your views here.

# remember, always include project info id.

from .forms import FileUploadForm, PermChoiceForm
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.decorators import login_required
from project_info.models import ProjectInfo, Message
from file_info.models import FileInfo, UniqueFile

from .utils import gen_MD5_of_UploadedFile, message_judge_func

from prototype.decorators import require_user_in
from prototype.utils import extract_from_GET, url_with_querystring
from project_info.utils import judge_func as project_judge_func


@login_required
@require_user_in(
        project_judge_func,
        'project_info_id', 
        (ProjectInfo, True, ('normal_group',))
)
def create_message(request, project_info_id, message_id):
    project_info_id = int(project_info_id)
    project_info = get_object_or_404(ProjectInfo, id=project_info_id)
    if message_id == None:
        # create_message
        message = Message(project_info=project_info,
                          creator=request.user)
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

            # check unique
            md5 = gen_MD5_of_UploadedFile(uploaded_file)
            unique_file = UniqueFile.objects.filter(md5=md5)
            if not unique_file:
                unique_file = UniqueFile(md5=md5)
                unique_file.save()
                unique_file.file.save(md5, uploaded_file)
            else:
                unique_file = unique_file[0]
            # save file info
            file_info = FileInfo(file_name=uploaded_file.name,
                                 owner_perm=owner_perm,
                                 group_perm=group_perm,
                                 everyone_perm=everyone_perm,
                                 unique_file=unique_file)
            file_info.save()
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


@login_required
@require_user_in(
        message_judge_func,
        'message_id', 
        (Message, True, (None,))
)
def delete_file_from_message(
        request, project_info_id, message_id,
        file_info_id):
    project_info_id = int(project_info_id)
    message_id = int(message_id)
    file_info_id = int(file_info_id)
    message = get_object_or_404(Message, id=message_id)
    file_info = get_object_or_404(message.file_info, id=file_info_id)

    # once a ForeignKey is delete, 
    # its related entity will remove the link as well.
    file_info.delete()

    # judge to remove unique file
    unique_file = file_info.unique_file
    if unique_file.fileinfo_set.count() == 0:
        unique_file.delete()

    return redirect('create_message_page',
                    project_info_id=project_info_id,
                    message_id=message.id)





