from django.urls import path

from ..views import RegisterAPIView, VerifyEmailAPIView


urlpatterns = [
    path('', RegisterAPIView.as_view()),
    path('verify', VerifyEmailAPIView.as_view(), name='verify_registration')
]