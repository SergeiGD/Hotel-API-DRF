from django.urls import path, include
from rest_framework import routers

from ..views import PermissionsViewSet


router = routers.SimpleRouter()
router.register(r'', PermissionsViewSet)


urlpatterns = [
    path('', include(router.urls))
]