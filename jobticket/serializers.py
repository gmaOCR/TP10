from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from .models import Project, Issue, Comment, Contributor
from rest_framework import serializers

User = get_user_model()


class ProjectListSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'title', 'type']


class ProjectDetailSerializer(serializers.ModelSerializer):
    # author_user = serializers.CharField(source='author_user.email')
    author_user = serializers.CharField(source='author_user.email', read_only=False, required=False)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'author_user', 'type', 'contributors']

    def contributors(self, instance):
        queryset = instance.contributors.all()
        serializer = ContributorsDetailSerializer(queryset, many=True, read_only=True, required=False)
        return serializer.data

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.type = validated_data.get('type', instance.type)

        author_user_email = validated_data.get('author_user', None)
        if author_user_email:
            try:
                author_user = User.objects.get(email=author_user_email)
                instance.author_user = author_user
            except User.DoesNotExist:
                pass

        instance.save()
        return instance

    def create(self, validated_data):
        validated_data['author_user'] = self.context['request'].user
        return super().create(validated_data)


class IssueDetailSerializer(ModelSerializer):
    author_user = serializers.CharField(source='author_user.email')
    assigned_to = serializers.CharField(source='assigned_to.email')
    project = serializers.CharField(source='project.title')

    class Meta:
        model = Issue
        fields = ['id', 'title', 'desc', 'tag', 'priority', 'status', 'project', 'author_user', 'assigned_to',
                  'comments', 'created_time']

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.desc = validated_data.get('desc', instance.desc)
        instance.tag = validated_data.get('tag', instance.tag)
        instance.priority = validated_data.get('priority', instance.priority)
        instance.status = validated_data.get('status', instance.status)

        if 'assigned_to' in validated_data:
            assigned_to_email = validated_data.pop('assigned_to')
            try:
                assigned_to_user = User.objects.get(email=assigned_to_email['email'])
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "User with email {} does not exist.".format(assigned_to_email['email']))

            project = instance.project
            if not project.contributors.filter(user=assigned_to_user).exists():
                raise serializers.ValidationError(
                    "User with email {} is not a contributor of the project.".format(assigned_to_email['email']))


            instance.assigned_to = assigned_to_user

        # 'project', 'author_user' and 'created_time' fields should not change
        instance.save(update_fields=['title', 'desc', 'tag', 'priority', 'status', 'assigned_to'])

        return instance

    def validate_tag(self, value):
        choices = [choice[0] for choice in Issue.TAG_CHOICES]
        if value not in choices:
            raise serializers.ValidationError(
                _('This is not a valid choice for Tag.')
            )
        return value

    def validate_priority(self, value):
        choices = [choice[0] for choice in Issue.PRIORITY_CHOICES]
        if value not in choices:
            raise serializers.ValidationError(
                _('This is not a valid choice for Priority.')
            )
        return value

    def validate_status(self, value):
        choices = [choice[0] for choice in Issue.STATUS_CHOICES]
        if value not in choices:
            raise serializers.ValidationError(
                _('This is not a valid choice for Status.')
            )
        return value


class IssueListSerializer(ModelSerializer):
    author_user = serializers.CharField(source='author_user.email', read_only=False, required=False)

    class Meta:
        model = Issue
        fields = ['id', 'title', 'desc', 'tag', 'priority', 'status', 'author_user']


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
    author_user = serializers.CharField(source='author_user.email')
    issue = serializers.CharField(source='issue.title')

    class Meta:
        model = Comment
        fields = ['id', 'author_user', 'issue']


class CommentDetailSerializer(ModelSerializer):
    author_user = serializers.CharField(source='author_user.email')
    issue = serializers.CharField(source='issue.title')

    class Meta:
        model = Comment
        fields = ['issue', 'desc', 'author_user', 'created_time']

    def update(self, instance, validated_data):
        instance.desc = validated_data.get('desc', instance.desc)
        instance.issue = validated_data.get('issue', instance.issue)

        if 'author_user' in validated_data:
            author_user_email = validated_data.pop('author_user')
            author_user = User.objects.get(email=author_user_email['email'])
            instance.author_user = author_user

        # 'project', 'author_user' and 'created_time' fields should not change
        instance.save(update_fields=['desc', 'author_user', 'issue'])

        return instance
