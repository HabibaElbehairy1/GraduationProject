from django.urls import path
from .views import PredictViewSet

urlpatterns = [
    path("predict/", PredictViewSet.as_view({'post': 'create'}), name="predict"),
]
