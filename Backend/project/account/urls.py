from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.get_user, name='profile'),
    path('update/', views.update_user,name='update_user'),
    path('change_password/', views.change_password,name='change_password'),
    path('get_otp/', views.get_otp, name='get_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),


]
