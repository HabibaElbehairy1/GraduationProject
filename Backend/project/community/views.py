# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from rest_framework.decorators import action

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAuthenticatedWithJWT

class PostViewSet(IsAuthenticatedWithJWT,viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'id'


    def get_permissions(self):
        """
        Allow anyone to list or retrieve posts. Other ac
        tions require authentication.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if request.user == post.user or request.user.is_staff:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)


from rest_framework.permissions import AllowAny, IsAuthenticated

class CommentViewSet(IsAuthenticatedWithJWT,viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return Comment.objects.filter(post__id=post_id)
        return Comment.objects.all()


    def get_permissions(self):
        """
        Allow anyone to list or retrieve comments.
        Only authenticated users can create, update, or delete comments.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        post_id = self.kwargs['post_id']
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if request.user == comment.user or request.user.is_staff:
            return super().destroy(request, *args, **kwargs)
        return Response(status=status.HTTP_403_FORBIDDEN)
