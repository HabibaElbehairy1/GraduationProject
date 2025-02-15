from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.get_user, name='profile'),
    path('update/', views.update_user,name='update_user'), 

]
