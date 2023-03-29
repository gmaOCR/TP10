from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model, login, authenticate
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied

from .models import Project, Issue, Comment, Contributor
from .serializers import ProjectListSerializer, ProjectDetailSerializer, IssueListSerializer, IssueDetailSerializer, \
    CommentDetailSerializer, CommentListSerializer, ContributorsDetailSerializer, ContributorsListSerializer, \
    UserSerializer

User = get_user_model()


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.owner == request.user


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        return Project.objects.filter(Q(author_user=self.request.user) |
                                      Q(contributor_project__user=self.request.user)).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        elif self.action == 'create':
            return self.detail_serializer_class
        return super(ProjectViewSet, self).get_serializer_class()

    @action(detail=False, methods=['post'])
    def create_project(self, request):
        serializer = ProjectDetailSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(author_user=request.user)
            response_serializer = ProjectListSerializer(project)
            return Response(response_serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class ContributorViewSet(ModelViewSet):
    serializer_class = ContributorsDetailSerializer
    list_serializer_class = ContributorsListSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        if self.action == 'create':
            permissions.append(IsAuthenticated())
        else:
            permissions.append(IsOwnerOrReadOnly())
        return permissions

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if user.is_authenticated:
            if user == project.author_user or user in project.contributors.all():
                return project.contributors.select_related('user')
        raise PermissionDenied(detail='You do not have permission to access this resource.')

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id')
        if project_id is None:
            return Response({'error': 'project_id is required'}, status=400)
        project = get_object_or_404(Project, pk=project_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)
        return Response(serializer.data, status=201)


class IssueViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs['project_id'])
        return Issue.objects.filter(project=project)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        project_id = self.kwargs.get('project_id', None)
        if project_id is None:
            return Response({"error": "project_id is required"}, status=400)
        project = get_object_or_404(Project, pk=project_id)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['project'] = project
            serializer.validated_data['author_user'] = request.user
            serializer.validated_data['assigned_to'] = request.user
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers)
        else:
            return Response(serializer.errors, status=400)


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentListSerializer
    detail_serializer_class = CommentDetailSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            Q(author_user=self.request.user) | Q(contributor_project__user=self.request.user)
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        return super().get_serializer_class()


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                'message': 'User registered successfully',
                'user_id': user.id,
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Handle user login.
    """

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return Response({'token': user.auth_token.key})
            else:
                return Response({'error': 'User account has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid login credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
