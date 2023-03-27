from rest_framework.serializers import ModelSerializer
from .models import Project, Issue, Comment, Contributor


class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'type', 'title']


class ProjectDetailSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'type', 'title', 'description']


class IssueDetailSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'desc', 'tag', 'priority', 'status', 'author_user', 'assigned_to', 'created_time']


class IssueListSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'title', 'tag', 'priority', 'status']

class Contributors(ModelSerializer):
    pass