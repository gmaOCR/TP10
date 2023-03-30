from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from rest_framework import status
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model, login, authenticate
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed

from .models import Project, Issue, Comment, Contributor
from .serializers import ProjectListSerializer, ProjectDetailSerializer, IssueListSerializer, IssueDetailSerializer, \
    CommentDetailSerializer, CommentListSerializer, ContributorsDetailSerializer, ContributorsListSerializer, \
    UserSerializer

User = get_user_model()


class IsAuthorOrContributor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if isinstance(obj, Project):
            return obj.author_user == request.user or obj.contributors.filter(user=request.user,
                                                                              permission='CRUD').exists()
        elif isinstance(obj, Contributor):
            return obj.user == request.user or obj.project.author_user == request.user or obj.permission == 'CRUD'
        return False


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthorOrContributor]

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        return Project.objects.filter(Q(author_user=self.request.user) |
                                      Q(contributors__user=self.request.user)).distinct()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        elif self.action == 'list':
            return self.serializer_class
        elif self.action == 'create':
            return self.serializer_class
        return super(ProjectViewSet, self).get_serializer_class()

    def create(self, request):
        serializer = ProjectListSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(author_user=request.user)
            contributor, created = Contributor.objects.get_or_create(
                project=project,
                user=request.user,
                defaults={'role': 'Responsable', 'permission': 'Full'}
            )
            if created:
                return Response(self.detail_serializer_class(project).data, status=201)
            else:
                return Response({"error": "User is already a contributor for this project."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=400)


class ContributorViewSet(ModelViewSet):
    detail_serializer_class = ContributorsDetailSerializer
    serializer_class = ContributorsListSerializer

    permission_classes = [IsAuthorOrContributor]

    def get_queryset(self):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        user = self.request.user
        if user.is_authenticated:
            if user == project.author_user:
                return project.contributors.select_related('user')
            elif project.contributors.filter(user=user).exists():
                return project.contributors.filter(user=user).select_related('user')
        raise PermissionDenied(detail='You do not have permission to access this resource.')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.detail_serializer_class
        elif self.action == 'list':
            return self.serializer_class
        elif self.action == 'create':
            return self.serializer_class
        return super(ContributorViewSet, self).get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data['user']['email']
        user = get_object_or_404(User, email=user_email)

        project_id = self.kwargs.get('project_id')
        project = get_object_or_404(Project, id=project_id)

        if project.contributors.filter(user=user).exists():
            return Response({"error": "User is already a contributor for this project."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer.validated_data['user'] = user
        serializer.validated_data['permission'] = 'Create & Read'
        serializer.validated_data['role'] = 'Contributeur'
        serializer.validated_data['project'] = project

        contributor = serializer.save()

        serialized_contributor = ContributorsListSerializer(contributor).data
        return Response(serialized_contributor, status=201)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        user = request.user

        if user != project.author_user:
            raise PermissionDenied(detail='You do not have permission to perform this action.')

        if instance.user == user:
            self.perform_destroy(instance)
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif instance.role == 'Responsable':
            raise PermissionDenied(detail='You do not have permission to perform this action.')
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT', detail='This endpoint does not support the PUT method.')


class IssueViewSet(ModelViewSet):
    permission_classes = [IsAuthorOrContributor]
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
            Q(author_user=self.request.user) | Q(contributors__user=self.request.user)
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


def my_login_view(request):
    if request.user.is_authenticated:
        return redirect('/api/projects/')
    else:
        return redirect('login')


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
                return redirect('/api/projects/')
                # return Response({'token': user.auth_token.key})
            else:
                return Response({'error': 'User account has been disabled.'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': 'Invalid login credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
