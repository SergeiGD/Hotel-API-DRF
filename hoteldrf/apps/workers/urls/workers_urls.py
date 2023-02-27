from django.urls import path, include
from rest_framework import routers

from ..views import WorkersViewSet


router = routers.SimpleRouter()
router.register(r'', WorkersViewSet)

urlpatterns = [
    path('', include(router.urls))
]