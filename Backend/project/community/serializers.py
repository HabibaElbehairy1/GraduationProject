from rest_framework import serializers
from .models import Post, Comment
from django.contrib.auth import get_user_model
User = get_user_model() 

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested user details
    class Meta:
        model = Comment
        fields = ['user','comment', 'created_at', 'updated_at']
        read_only_fields = ['user']

class PostSerializer(serializers.ModelSerializer):
    comment = CommentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)  # Nested user details   
    class Meta:
        model = Post
        fields = ['post_name' ,'user', 'content', 'image', 'created_at', 'updated_at', 'comment']
        read_only_fields = ['user']


