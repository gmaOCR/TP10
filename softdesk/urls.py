from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from jobticket.views import ProjectViewSet, CommentViewSet, IssueViewSet, ContributorViewSet
from authentication.views import login,signup

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename="projects")
router.register(r'projects/(?P<project_id>\d+)/issues', IssueViewSet, basename='project-issues')
router.register(r'projects/(?P<project_id>\d+)/users', ContributorViewSet, basename='project-contributors')
router.register(r'projects/(?P<project_id>\d+)/issues/(?P<issue_id>\d+)/comments/', CommentViewSet, basename='project-comments')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/login/', login, name='login'),
    path('api/', include(router.urls), name='api'),
    path('api/signup/', signup, name='signup'),
]

urlpatterns += router.urls
