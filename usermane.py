import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import CustomUser


user = '+998931004005'

try:
    user_r = CustomUser.objects.filter(phone=user).first()
    user_r.is_active = True
    user_r.is_staff = True
    user_r.is_superuser = True
    user_r.set_password('1234')
    user_r.save()
    print(user_r.is_staff,user_r.is_superuser)
except:
    pass