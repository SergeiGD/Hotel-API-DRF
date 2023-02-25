from django.urls import path

from ..views import WorkersListAPIView, WorkersManageAPIView


urlpatterns = [
    path('', WorkersListAPIView.as_view()),
    path('<int:pk>', WorkersManageAPIView.as_view()),
]