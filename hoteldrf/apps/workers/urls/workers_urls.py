from django.urls import path, include
from rest_framework import routers

from ..views import WorkersViewSet, WorkerTimetablesListAPIView, WorkerTimetableManageAPIView, WorkerGroupsListAPIView,\
                    WorkerGroupDeleteAPIView


router = routers.SimpleRouter()
router.register(r'', WorkersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/timetables/', WorkerTimetablesListAPIView.as_view()),
    path('<int:pk>/timetables/<int:timetable_id>/', WorkerTimetableManageAPIView.as_view()),
    path('<int:pk>/groups/', WorkerGroupsListAPIView.as_view()),
    path('<int:pk>/groups/<int:group_id>/', WorkerGroupDeleteAPIView.as_view()),
]
