from django.contrib.auth.models import User
User.objects.create_user('peter', password='123456')
User.objects.create_user('john', password='123456')
User.objects.create_user('kate', password='123456')
