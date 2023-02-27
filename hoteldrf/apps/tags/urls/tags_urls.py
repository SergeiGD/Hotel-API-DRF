from django.urls import path, include
from rest_framework import routers

from ..views import TagsViewSet


router = routers.SimpleRouter()
router.register(r'', TagsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
