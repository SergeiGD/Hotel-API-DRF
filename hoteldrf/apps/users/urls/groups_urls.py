from django.urls import path, include
from rest_framework import routers

from ..views import GroupsViewSet, RolePermissionsListAPIView, RolePermissionDeleteAPIView


router = routers.SimpleRouter()
router.register(r'', GroupsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/permissions/', RolePermissionsListAPIView.as_view()),
    path('<int:pk>/permissions/<int:permission_id>', RolePermissionDeleteAPIView.as_view()),
]