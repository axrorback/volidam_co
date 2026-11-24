from django.urls import path
from .views import *

urlpatterns = [
    path('eskiz-sms-callback/', eskiz_sms_callback, name='eskiz_sms_callback'),
    path('login/', phone_login, name='login'),
    path('verify/', verify_phone, name='verify_phone'),
    path('profile/', profile, name='profile'),
    path('onboarding/', profile_onboarding, name='onboarding')
]