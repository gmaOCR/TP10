from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated

from .permissions import IsAuthor, IsContributor
from .models import Project, Issue, Comment, Contributor
from .serializers import (ProjectListSerializer, ProjectDetailSerializer,
                          IssueListSerializer, IssueDetailSerializer,
                          CommentDetailSerializer, CommentListSerializer,
                          ContributorsDetailSerializer, ContributorsListSerializer)

User = get_user_model()


class ProjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAuthor]

    serializer_class = ProjectListSerializer
    detail_serializer_class = ProjectDetailSerializer

    def get_queryset(self):
        return Project.objects.filter(Q(author_user=self.request.user) |
                                      Q(contributors__user=self.request.user)).distinct()

    def get_serializer_class(self):
        print('Action used:', self.action)
        if self.action == 'update':
            return self.detail_serializer_class
        elif self.action == 'create':
            return self.detail_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class
        elif self.action == 'list':
            return self.serializer_class
        return super(ProjectViewSet, self).get_serializer_class()

    def create(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = ProjectDetailSerializer(data=request.data)
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

    def destroy(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)
        project.delete()
        return Response(
            {'message': 'The project has been deleted'},
            status=status.HTTP_200_OK,
        )

    def update(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        self.check_object_permissions(request, project)
        data = request.data
        data['author_user'] = request.user.id
        serializer = self.get_serializer(project, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'The project has been updated'}, status=status.HTTP_200_OK)


class ContributorViewSet(ModelViewSet):
    detail_serializer_class = ContributorsDetailSerializer
    serializer_class = ContributorsListSerializer

    permission_classes = [IsAuthenticated, IsAuthor]

    def get_queryset(self):
        return Contributor.objects.filter(project=self.kwargs['project_id'])

    def get_serializer_class(self):
        print('Action used:', self.action)
        if self.action == 'retrieve':
            raise MethodNotAllowed('RETRIEVE', detail='This endpoint does not support this method.')
        return super(ContributorViewSet, self).get_serializer_class()

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, id=self.kwargs.get('project_id'))
        self.check_object_permissions(request, project)

        # Get email from POST request data
        email = request.data.get('email')
        if not email:
            raise ValidationError({'email': 'This field is required.'})

        # Get user from email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise ValidationError({'email': f'User with email "{email}" not found.'})

        # Check if user is already a contributor
        if project.contributors.filter(user=user).exists():
            raise ValidationError({'email': f'User with email "{email}" is already a contributor.'})

        # Add user as a contributor to the project with default role and permission values
        contributor = project.contributors.create(user=user, permission='Create & Read', role='Contributeur')

        # Return created contributor object
        serializer = self.get_serializer(contributor)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, project_id=None, pk=None):
        try:
            contributor = Contributor.objects.get(pk=pk, project__pk=project_id)
            self.check_object_permissions(request, contributor)
            contributor.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Contributor.DoesNotExist:
            return Response({"message": "Issue not found."}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT', detail='This endpoint does not support the PUT method.')


class IssueViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsContributor]
    serializer_class = IssueListSerializer
    detail_serializer_class = IssueDetailSerializer

    def get_queryset(self):
        contributor_projects = Project.objects.filter(
            Q(contributors__user_id=self.request.user)
            | Q(author_user=self.request.user)
        )
        return Issue.objects.filter(
            project=self.kwargs['project_id'],
            project__in=contributor_projects,
        )

    def get_serializer_class(self):
        print('Action used:', self.action)
        if self.action == 'retrieve' or self.action == 'update':
            return self.detail_serializer_class
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        # Récupérer l'objet Project correspondant à l'identificateur de projet fourni dans l'URL
        project_id = self.kwargs.get('project_id', None)
        if project_id is None:
            return Response({"error": "project_id is required"}, status=400)
        project = get_object_or_404(Project, pk=project_id)

        # Vérifier que l'utilisateur courant a les permissions appropriées pour créer l'objet Issue
        self.check_object_permissions(request, project)

        # Vérifier que les données entrées par l'utilisateur sont valides
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Ajouter la `project`, l'`author_user` et l'`assigned_to` aux données valides
        validated_data = {
            'project': project,
            'author_user': request.user,
            'assigned_to': request.user,
            **serializer.validated_data
        }

        # Créer l'instance `Issue` avec les données valides
        instance = Issue.objects.create(**validated_data)

        # Retourner la réponse avec la nouvelle instance `Issue`
        serializer = IssueDetailSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # Retrieve the instance to update
        instance = self.get_object()
        self.check_object_permissions(instance)

        # Validate the request data
        serializer = IssueDetailSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Save the updated instance
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=self.kwargs['pk'])
        self.check_object_permissions(request, issue)
        issue.delete()
        return Response(
            {'message': 'The issue has been deleted'},
            status=status.HTTP_200_OK,
        )


class CommentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsContributor, IsAuthor]
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
