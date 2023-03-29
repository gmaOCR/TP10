from django.contrib import admin
from django.db.models import Count

from authentication.admin import UserAdmin
from authentication.models import User
from .models import Project, Contributor, Issue, Comment


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'type', 'author_user')

    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        qs = qs.annotate(Count('contributor_project'))
        return qs

    def project_contributor_count(self, obj):
        return obj.contributor_project__count

    project_contributor_count.admin_order_field = 'contributor_project__count'
    project_contributor_count.short_description = 'Contributors'

    def __repr__(self):
        return f"{self.title} - {self.type}"


class ContributorAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'permission', 'project')

    def __repr__(self):
        return f"{self.user} - {self.role}"


class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'desc', 'project', 'tag', 'priority', 'status', 'author_user', 'assigned_to', 'created_time')

    def __repr__(self):
        return f"{self.title} - {self.tag} ({self.priority})"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('desc', 'author_user', 'issue', 'created_time')

    def __repr__(self):
        return f"{self.desc} - {self.issue}"


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_superuser', 'is_admin')

    def is_admin(self, obj):
        return obj.is_staff and obj.is_superuser

    is_admin.boolean = True
    is_admin.short_description = 'Admin status'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Contributor, ContributorAdmin)
admin.site.register(Project, ProjectAdmin)
