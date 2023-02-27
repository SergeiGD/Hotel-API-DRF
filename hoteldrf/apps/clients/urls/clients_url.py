from django.urls import path, include
from rest_framework import routers

from ..views import ClientsViewSet


router = routers.SimpleRouter()
router.register(r'', ClientsViewSet)

urlpatterns = [
    path('', include(router.urls))
]
