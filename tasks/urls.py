from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, external_tasks_view

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('external-tasks/', external_tasks_view, name='external_tasks'),
]
