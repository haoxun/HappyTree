from __future__ import unicode_literals
from django.contrib.auth.models import User
from user_info.models import UserInfo
import hashlib

user_dict = {
    ('programmer.zhx@gmail.com', 'peter', '111111'),
    ('social.zhx@gmail.com', 'john', '111111'),
    ('academic.zhx@gmail.com', 'kate', '111111'),
}

# user

def hex_md5(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


for email, name, password in user_dict:
    username = hex_md5(email)
    password = hex_md5(password)
    user = User.objects.create_user(username=username, password=password)

    UserInfo.objects.create(user=user, email=email)

print "finish building"
