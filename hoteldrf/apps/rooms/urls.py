from django.urls import path

from .views import RoomsCategoriesListAPIView, RoomCategoryCreateAPIView, RoomCreateAPIView, RoomsListAPIView


urlpatterns = [
    path('', RoomsCategoriesListAPIView.as_view()),
    path('create/', RoomCategoryCreateAPIView.as_view()),
    path('<int:cat_id>/rooms/create', RoomCreateAPIView.as_view()),
    path('<int:cat_id>/rooms/', RoomsListAPIView.as_view()),
]
