from django.urls import path

from ..views import ClientOrdersListAPIView, ClientOrderManageAPIView, ClientPurchaseManageAPIView, \
                    ClientPurchasesListAPIView, ClientOrderPayAPIView


urlpatterns = [
    path('', ClientOrdersListAPIView.as_view()),
    path('<int:pk>/', ClientOrderManageAPIView.as_view()),
    path('<int:pk>/pay/', ClientOrderPayAPIView.as_view()),
    path('<int:pk>/purchases/', ClientPurchasesListAPIView.as_view()),
    path('<int:pk>/purchases/<int:purchase_id>/', ClientPurchaseManageAPIView.as_view()),
]
