from django.urls import path

from ..views import RoomsCategoriesListAPIView, RoomsListAPIView, photos_list_api_view, CategoryTagsListAPIView, \
    RoomCategoryManageAPIView, RoomManageAPIView, PhotoManageAPIView, CategoryTagManageAPIView \


urlpatterns = [
    path('', RoomsCategoriesListAPIView.as_view()),
    path('<int:pk>', RoomCategoryManageAPIView.as_view()),
    path('<int:cat_id>/rooms', RoomsListAPIView.as_view()),
    path('<int:cat_id>/rooms/<int:pk>', RoomManageAPIView.as_view()),
    path('<int:cat_id>/photos', photos_list_api_view),
    path('<int:cat_id>/photos/<int:pk>', PhotoManageAPIView.as_view()),
    path('<int:cat_id>/tags', CategoryTagsListAPIView.as_view()),
    path('<int:cat_id>/tags/<int:pk>', CategoryTagManageAPIView.as_view())
]
