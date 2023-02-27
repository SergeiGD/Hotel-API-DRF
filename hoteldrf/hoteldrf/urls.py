"""hoteldrf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/rooms_cats/', include('apps.rooms.urls.categories_urls')),
    path('api/tags/', include('apps.tags.urls.tags_urls')),
    path('api/workers/', include('apps.workers.urls.workers_urls')),
    path('api/orders/', include('apps.orders.urls.orders_urls')),
    path('api/sales/', include('apps.sales.urls.sales_urls')),
    path('api/clients/', include('apps.clients.urls.clients_url')),
    path('api/registration/', include('apps.clients.urls.registration_urls')),
    path('api/login/', include('apps.users.urls.login_urls')),
]
