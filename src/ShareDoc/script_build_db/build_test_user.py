from __future__ import unicode_literals
from django.contrib.auth.models import User
from user_info.models import UserInfo
# user
u1 = User.objects.create_user('peter', password='123456')
u2 = User.objects.create_user('john', password='123456')
u3 = User.objects.create_user('kate', password='123456')

UserInfo.objects.create(
    user=u1,
    email="programmer.zhx@gmail.com"
) 
UserInfo.objects.create(
    user=u2,
    email="social.zhx@gmail.com"
) 
UserInfo.objects.create(
    user=u3,
    email="academic.zhx@gmail.com"
) 

print 'finish building'
