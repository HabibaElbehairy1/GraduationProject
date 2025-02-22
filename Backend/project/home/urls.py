from django.urls import path
from .views import ContactUsView, ReviewListCreateView

urlpatterns = [
    path('contact/', ContactUsView.as_view(), name='contact-us'),
    path('reviews/', ReviewListCreateView.as_view(), name='review'),
]