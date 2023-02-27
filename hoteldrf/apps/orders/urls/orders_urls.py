from django.urls import path

from ..views import PurchasesListAPIView, OrdersListAPIView, OrderManageAPIView, PurchaseManageAPIView


urlpatterns = [
    path('', OrdersListAPIView.as_view()),
    path('<int:pk>', OrderManageAPIView.as_view()),
    path('<int:pk>/purchases', PurchasesListAPIView.as_view()),
    path('<int:pk>/purchases/<int:purchase_id>', PurchaseManageAPIView.as_view()),
]
