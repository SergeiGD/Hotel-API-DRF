from django.urls import path, include

from ..views import ClientProfileInfo


urlpatterns = [
    path('info/', ClientProfileInfo.as_view()),
    path('orders/', include('apps.clients.urls.client_orders_urls')),
]
