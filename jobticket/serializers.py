from django.contrib.auth import get_user_model, authenticate
from rest_framework.serializers import ModelSerializer
from .models import Project, Issue, Comment, Contributor
from rest_framework import serializers

User = get_user_model()


class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'type']


class ProjectDetailSerializer(ModelSerializer):
    author_user = serializers.CharField(source='author_user.email')

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'author_user', 'type']


class IssueDetailSerializer(ModelSerializer):
    author_user = serializers.CharField(source='author_user.email')
    assigned_to = serializers.CharField(source='assigned_to.email')

    class Meta:
        model = Issue
        fields = ['id', 'title', 'desc', 'tag', 'priority', 'status', 'author_user', 'assigned_to', 'created_time']


class IssueListSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'desc', 'tag', 'priority', 'status']


class ContributorsDetailSerializer(ModelSerializer):
    user = serializers.CharField(source="user.email")
    project = serializers.CharField(source="project.title")

    class Meta:
        model = Contributor
        fields = ['id', 'role', 'user', 'project', 'permission']


class ContributorsListSerializer(ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source="user.email")

    class Meta:
        model = Contributor
        fields = ['id', 'user']


class CommentListSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['author_user', 'issue']


class CommentDetailSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['desc', 'author_user', 'issue', 'created_time']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(username=email, password=password)
        if user and user.is_active:
            data['user'] = user
        else:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        return data
