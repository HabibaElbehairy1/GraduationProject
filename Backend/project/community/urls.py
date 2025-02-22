# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, CommentViewSet

router = DefaultRouter()
router.register('posts', PostViewSet)
router.register(r'posts/(?P<post_id>[0-9a-fA-F-]+)/comments', CommentViewSet, basename='post-comments')
router.register(r'comments', CommentViewSet, basename='all-comments')
urlpatterns = [
    path('', include(router.urls)),
]
