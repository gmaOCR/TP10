"""softdesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.urls import path, include
from rest_framework import routers

from jobticket.views import ProjectViewSet, UserViewSet, LoginView, CommentViewSet, IssueViewSet, ContributorViewSet

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename="projects")
router.register('users', UserViewSet, basename="users")
router.register(r'projects/(?P<project_id>\d+)/issues', IssueViewSet, basename='project-issues')
router.register(r'projects/(?P<project_id>\d+)/users', ContributorViewSet, basename='project-contrib')
router.register(r'projects/(?P<project_id>\d+)/users/(?P<user_id>\d+)/', ContributorViewSet, basename='project'
                                                                                                      '-contributors')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api-auth/login/', LoginView.as_view(), name='login'),
    path('api/', include(router.urls), name='api'),
    path('api/signup/', UserViewSet.as_view({'post': 'signup'}), name='signup'),
]

urlpatterns += router.urls
