# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def show_root(request):
    return render(request, 'user_status/root.html', {'user' : request.user})
