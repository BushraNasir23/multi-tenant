from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer
from .permissions import SameCompanyPermission

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, SameCompanyPermission]

    def get_queryset(self):
        user = self.request.user
        if user.company:
            return Task.objects.filter(company=user.company)
        return Task.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"company_{task.company.id}",
            {
                "type": "task_created",
                "task": TaskSerializer(task).data
            }
        )

    def perform_update(self, serializer):
        task = serializer.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"company_{task.company.id}",
            {
                "type": "task_updated",
                "task": TaskSerializer(task).data
            }
        )

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to current user"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics for the company"""
        queryset = self.get_queryset()
        stats = {
            'total_tasks': queryset.count(),
            'by_status': dict(queryset.values_list('status').annotate(count=Count('status'))),
            'by_user': dict(queryset.values_list('assigned_to__username').annotate(count=Count('assigned_to')))
        }
        return Response(stats)

import requests
import asyncio

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def external_tasks_view(request):
    """Sync endpoint that fetches external data and merges with local tasks"""
    try:
        response = requests.get('https://jsonplaceholder.typicode.com/todos', timeout=10)
        external_tasks = response.json()[:5] 
        
        user = request.user
        if user.company:
            local_tasks = Task.objects.filter(company=user.company)[:5]
            local_tasks_data = TaskSerializer(local_tasks, many=True).data
        else:
            local_tasks_data = []
        
        merged_data = {
            'local_tasks': local_tasks_data,
            'external_tasks': [
                {
                    'id': task['id'],
                    'title': task['title'],
                    'completed': task['completed'],
                    'source': 'external'
                }
                for task in external_tasks
            ]
        }
        
        return Response(merged_data)
    
    except Exception as e:
        return Response(
            {'error': f'Failed to fetch external data: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )