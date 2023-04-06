from rest_framework.permissions import BasePermission
from .models import Project, Contributor


def project_contributor(request, obj):
    is_project_contributor = Project.objects.filter(
        contributors__project_id=obj.id,
        contributors__user_id=request.user.id,
    )
    is_project_author = obj.author_user == request.user
    return is_project_contributor or is_project_author


class IsAuthor(BasePermission):
    """Permission to check if the authenticated user is the author of the project."""

    message = "You're not allowed because you're not the author."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Contributor):
            return bool(obj.user == request.user)
        elif obj.author_user == request.user:
            return bool(obj.author_user == request.user)
        return False


class IsContributor(BasePermission):
    """Permission to check if the authenticated user is a contributor with CRUD permissions on the project."""

    message = "You're not allowed because you're not the author or a contributor of the project."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if project_contributor(request, obj):
            return True
        return False
