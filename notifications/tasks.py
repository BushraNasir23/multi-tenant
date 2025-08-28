from celery import shared_task
from django.conf import settings
from .models import EmailNotification
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_task_notification_email(task_id, recipient_id):
    try:
        from tasks.models import Task
        from accounts.models import User
        
        task = Task.objects.get(id=task_id)
        recipient = User.objects.get(id=recipient_id)
        subject = f"New Task Assigned: {task.title}"
        message = f"""
        Hello {recipient.first_name or recipient.username},
        
        You have been assigned a new task:
        
        Title: {task.title}
        Description: {task.description}
        Status: {task.get_status_display()}
        Created by: {task.created_by.get_full_name() or task.created_by.username}
        Company: {task.company.name}
        
        Please log in to the task manager to view more details.
        
        Best regards,
        Task Manager Team
        """
        
        notification = EmailNotification.objects.create(
            recipient=recipient,
            subject=subject,
            message=message,
            task=task
        )
        logger.info(f"EMAIL NOTIFICATION SENT:")
        logger.info(f"To: {recipient.email}")
        logger.info(f"Subject: {subject}")
        logger.info(f"Message: {message}")
        
        notification.is_sent = True
        notification.save()
        
        return f"Email notification sent to {recipient.email}"
        
    except Exception as e:
        logger.error(f"Failed to send email notification: {str(e)}")
        return f"Failed to send email: {str(e)}"
