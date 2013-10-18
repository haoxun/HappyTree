from __future__ import unicode_literals
# django dependency
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
# auth dependency
from django.contrib.auth.decorators import login_required
from guardian.decorators import permission_required_or_403, permission_required
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms, \
                               get_objects_for_user
# model 
from guardian.models import User, Group
from project.models import Message, Project
from file_storage.models import UniqueFile, FilePointer
# form
from file_storage.forms import ProjectChoiceForm, FileUploadForm, MessageInfoForm
# decorator
# util
from file_storage.utils import gen_MD5_of_UploadedFile
# python library
from datetime import datetime



@login_required
def init_message_page(request):
    project_set = get_objects_for_user(request.user, 'project.project_upload')
    if len(project_set) == 0:
        # after finish dev, should give some error message about that,
        # instead of raising PermissionDenied
        raise PermissionDenied
    message = Message.objects.create(project=project_set[0])
    assign_perm('message_ownership', request.user, message)
    return redirect('create_message_page', message_id=message.id)

@permission_required_or_403('project.message_ownership', (Message, 'id', 'message_id'))
def create_message_page(request, message_id):
    message = get_object_or_404(Message, id=int(message_id))
    project_set = get_objects_for_user(request.user, 'project.project_upload')

    if request.method == 'POST':
        form_select_project = ProjectChoiceForm(project_set, request.POST)
        form_file_upload = FileUploadForm(request.POST, request.FILES)
        form_post_message = MessageInfoForm(request.POST)
        
        if form_file_upload.is_valid():
            uploaded_file = request.FILES['uploaded_file']
            md5 = gen_MD5_of_UploadedFile(uploaded_file)
            # get unique file
            unique_file = UniqueFile.objects.filter(md5=md5)
            if not unique_file:
                # create unique file
                unique_file = UniqueFile.objects.create(md5=md5)
                # save md5 as its filename
                unique_file.file.save(md5, uploaded_file)
            else:
                unique_file = unique_file[0]
            # gen file pointer
            file_pointer = FilePointer.objects.create(
                                name=uploaded_file.name,
                                unique_file=unique_file,
                                message=message)
            return redirect('create_message_page', message_id=message_id)

        if form_post_message.is_valid() and form_select_project.is_valid():
            # set message info
            message.title = form_post_message.cleaned_data['title']
            message.description = form_post_message.cleaned_data['description']
            # target project
            project_id = form_select_project.cleaned_data['project_id']
            message.project = get_object_or_404(Project, id=int(project_id))
            # set post
            message.post_flag = True
            message.save()
            return redirect('home_page')
    else:
        form_select_project = ProjectChoiceForm(project_set)
        form_file_upload = FileUploadForm()
        form_post_message = MessageInfoForm()

    render_data_dict = {
            'message': message,
            'form_select_project': form_select_project,
            'form_file_upload': form_file_upload,
            'form_post_message': form_post_message,
    }
    return render(request,
                  'file_storage/create_message_page.html',
                  render_data_dict)

@permission_required_or_403('project.message_ownership', (Message, 'id', 'message_id'))
def delete_file_pointer_from_message(request, message_id, file_pointer_id):
    message = get_object_or_404(Message, id=int(message_id))
    file_pointer = get_object_or_404(FilePointer, id=int(file_pointer_id))
    unique_file = file_pointer.unique_file

    # delete file pointer
    file_pointer.delete()
    # smart pointer
    if unique_file.file_pointers.count() == 0:
        unique_file.delete()
    return redirect('create_message_page', message_id=message_id)



            


    
    

