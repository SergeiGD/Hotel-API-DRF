from django.urls import path, include
from rest_framework import routers

from ..views import SalesViewSet, SaleAppliesToListAPIView, SaleAppliesToDeleteAPIView


router = routers.SimpleRouter()
router.register(r'', SalesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/applies_to/', SaleAppliesToListAPIView.as_view()),
    path('<int:pk>/applies_to/<cat_id>/', SaleAppliesToDeleteAPIView.as_view()),
]
