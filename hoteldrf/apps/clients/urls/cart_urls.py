from django.urls import path

from ..views import CartRetrieveAPIView, CartPurchasesManageAPIView, CartPurchasesCreateAPIView, \
                    CartPayAPIView, CartPayPrepaymentAPIView


urlpatterns = [
    path('', CartRetrieveAPIView.as_view()),
    path('add_item/', CartPurchasesCreateAPIView.as_view()),
    path('<int:purchase_id>/', CartPurchasesManageAPIView.as_view()),
    path('pay_prepayment/', CartPayPrepaymentAPIView.as_view()),
    path('pay/', CartPayAPIView.as_view()),
]
