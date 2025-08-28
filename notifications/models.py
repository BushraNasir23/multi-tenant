from django.db import models
from django.conf import settings

class EmailNotification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_notifications'
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Email to {self.recipient.username}: {self.subject}"