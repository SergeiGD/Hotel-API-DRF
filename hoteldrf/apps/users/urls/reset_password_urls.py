from django.urls import path

from ..views import RequestResetPasswordAPIView, PasswordTokenCheckAPIView


urlpatterns = [
    path('', RequestResetPasswordAPIView.as_view()),
    path('<uidb64>/<token>/', PasswordTokenCheckAPIView.as_view(), name='password-reset-confirm')
]