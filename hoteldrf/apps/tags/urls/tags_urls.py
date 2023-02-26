from django.urls import path

from ..views import TagsListAPIView, TagsCreateAPIView, TagsManageAPIView


urlpatterns = [
    path('', TagsListAPIView.as_view()),
    path('create', TagsCreateAPIView.as_view()),
    path('<int:pk>', TagsManageAPIView.as_view()),
]
