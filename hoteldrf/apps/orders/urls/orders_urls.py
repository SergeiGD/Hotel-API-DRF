from django.urls import path

from ..views import PurchasesListAPIView, OrdersListAPIView, OrderManageAPIView, PurchaseManageAPIView


urlpatterns = [
    path('', OrdersListAPIView.as_view()),
    path('<int:pk>', OrderManageAPIView.as_view()),
    path('<int:order_id>/purchases', PurchasesListAPIView.as_view()),
    path('<int:order_id>/purchases/<int:pk>', PurchaseManageAPIView.as_view()),
]
