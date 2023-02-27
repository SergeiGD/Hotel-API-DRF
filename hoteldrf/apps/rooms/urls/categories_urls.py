from django.urls import path, include
from rest_framework import routers

from ..views import RoomsCategoriesViewSet, RoomsListAPIView, photos_list_api_view, CategoryTagsListAPIView, \
    RoomManageAPIView, PhotoManageAPIView, CategoryTagManageAPIView \


router = routers.SimpleRouter()
router.register(r'', RoomsCategoriesViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/rooms', RoomsListAPIView.as_view()),
    path('<int:pk>/rooms/<int:room_id>', RoomManageAPIView.as_view()),
    path('<int:pk>/photos', photos_list_api_view),
    path('<int:pk>/photos/<int:photo_id>', PhotoManageAPIView.as_view()),
    path('<int:pk>/tags', CategoryTagsListAPIView.as_view()),
    path('<int:pk>/tags/<int:tag_id>', CategoryTagManageAPIView.as_view())
]
