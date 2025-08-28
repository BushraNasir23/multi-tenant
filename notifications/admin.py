from django.contrib import admin
from .models import EmailNotification

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'task', 'is_sent', 'sent_at']
    list_filter = ['is_sent', 'sent_at']
    search_fields = ['recipient__username', 'subject', 'task__title']
    readonly_fields = ['sent_at']