from __future__ import unicode_literals
from django.contrib.auth.models import User
from user_status.models import UserInfo
# user
u1 = User.objects.create_user('peter', password='123456')
u2 = User.objects.create_user('john', password='123456')
u3 = User.objects.create_user('kate', password='123456')

uinfo1 = UserInfo() 
uinfo2 = UserInfo() 
uinfo3 = UserInfo() 

uinfo1.user = u1
uinfo2.user = u2
uinfo3.user = u3

uinfo1.save()
uinfo2.save()
uinfo3.save()

