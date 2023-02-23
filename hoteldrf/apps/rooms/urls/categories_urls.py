from django.urls import path

from ..views import RoomsCategoriesListAPIView, RoomsListAPIView, PhotosListAPIView, \
    RoomCategoryCreateAPIView, RoomCreateAPIView, PhotoCreateAPIView,\
    RoomCategoryManageAPIView, RoomManageAPIView, PhotoManageAPIView


urlpatterns = [
    path('', RoomsCategoriesListAPIView.as_view()),
    path('create/', RoomCategoryCreateAPIView.as_view()),
    path('<int:pk>/', RoomCategoryManageAPIView.as_view()),
    path('<int:cat_id>/rooms/', RoomsListAPIView.as_view()),
    path('<int:cat_id>/rooms/create/', RoomCreateAPIView.as_view()),
    path('<int:cat_id>/rooms/<int:pk>/', RoomManageAPIView.as_view()),
    path('<int:cat_id>/photos/', PhotosListAPIView.as_view()),
    path('<int:cat_id>/photos/create/', PhotoCreateAPIView.as_view()),
    path('<int:cat_id>/photos/<int:pk>/', PhotoManageAPIView.as_view()),
]
