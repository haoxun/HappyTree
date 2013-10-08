# Create your views here.
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def show_root(request):
    return render(request, 'user_status/root.html', {'user': request.user})

@login_required
def logout_user(request):
    logout(request)
    return redirect('login_page')

