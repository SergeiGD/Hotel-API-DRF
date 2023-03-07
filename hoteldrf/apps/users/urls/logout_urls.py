from django.urls import path

from ..views import LogoutAPIView


urlpatterns = [
    path('', LogoutAPIView.as_view()),
]