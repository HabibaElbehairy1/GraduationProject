from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register_view'),
    path('profile/', views.GetUserView.as_view(), name='profile'),
    path('update/', views.UpdateUserView.as_view(),name='update_user'),
    path('change_password/', views.ChangePasswordView.as_view(),name='change_password'),
    path('get_otp/', views.get_otp, name='get_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),


]
