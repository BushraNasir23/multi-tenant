from django.core.management.base import BaseCommand
from django.db.models import Count, Q, Avg
from django.db.models.functions import TruncDate
from tasks.models import Task
from accounts.models import User, Company

class Command(BaseCommand):
    help = 'Display advanced task analytics using complex queries'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== TASK ANALYTICS ===\n'))
        self.stdout.write(self.style.WARNING('1. Tasks per User:'))
        user_task_counts = User.objects.annotate(
            total_tasks=Count('assigned_tasks'),
            completed_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status='done')),
            pending_tasks=Count('assigned_tasks', filter=Q(assigned_tasks__status__in=['todo', 'in_progress']))
        ).filter(total_tasks__gt=0).order_by('-total_tasks')

        for user in user_task_counts:
            self.stdout.write(
                f"  {user.username} ({user.company.name if user.company else 'No Company'}): "
                f"{user.total_tasks} total, {user.completed_tasks} completed, {user.pending_tasks} pending"
            )

        self.stdout.write(self.style.WARNING('\n2. Tasks by Status:'))
        total_tasks = Task.objects.count()
        status_counts = Task.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        for status in status_counts:
            percentage = (status['count'] / total_tasks * 100) if total_tasks > 0 else 0
            self.stdout.write(
                f"  {status['status'].title()}: {status['count']} tasks ({percentage:.1f}%)"
            )

       
        self.stdout.write(self.style.WARNING('\n3. Company Performance:'))
        company_stats = Company.objects.annotate(
            total_tasks=Count('tasks'),
            completed_tasks=Count('tasks', filter=Q(tasks__status='done')),
            total_users=Count('users'),
            avg_tasks_per_user=Avg('users__assigned_tasks__id')
        ).filter(total_tasks__gt=0).order_by('-total_tasks')

        for company in company_stats:
            completion_rate = (company.completed_tasks / company.total_tasks * 100) if company.total_tasks > 0 else 0
            self.stdout.write(
                f"  {company.name}: {company.total_tasks} tasks, "
                f"{company.completed_tasks} completed ({completion_rate:.1f}%), "
                f"{company.total_users} users"
            )

        self.stdout.write(self.style.WARNING('\n4. Daily Task Creation (Last 7 Days):'))
        daily_tasks = Task.objects.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('-date')[:7]

        for day in daily_tasks:
            self.stdout.write(f"  {day['date']}: {day['count']} tasks created")

    
        self.stdout.write(self.style.WARNING('\n5. Task Assignment Analysis:'))
        users_with_multiple_assignments = User.objects.annotate(
            assigned_count=Count('assigned_tasks')
        ).filter(assigned_count__gte=2).order_by('-assigned_count')

        for user in users_with_multiple_assignments:
            self.stdout.write(
                f"  {user.username}: {user.assigned_count} assigned tasks"
            )

        self.stdout.write(self.style.SUCCESS('\n=== END ANALYTICS ==='))
