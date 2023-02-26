from django.urls import path

from ..views import LoginAPIView, RefreshAPIView


urlpatterns = [
    path('', LoginAPIView.as_view()),
    path('refresh', RefreshAPIView.as_view()),
]