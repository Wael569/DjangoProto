"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from rest_framework.routers import DefaultRouter
from Sales.views import SalesDataViewSet, ETLPipelineAPIView, ETLPipelineAsyncAPIView

# Create router for viewsets
router = DefaultRouter()
router.register(r'sales', SalesDataViewSet, basename='sales')

urlpatterns = [
        path('api/etl/run-async/', ETLPipelineAsyncAPIView.as_view(), name='etl-run-async'),

    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/etl/run/', ETLPipelineAPIView.as_view(), name='etl-run'),
    path('api/etl/status/<str:task_id>/', ETLPipelineAsyncAPIView.as_view(), name='etl-status'),
]

