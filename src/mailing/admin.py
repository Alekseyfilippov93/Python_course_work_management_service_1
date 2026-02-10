from django.contrib import admin, messages
from .services import run_mailing
from mailing.models import Recipient, Message, Mailing, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "full_name")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("subject",)
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "status")
    list_filter = ("status",)
    filter_horizontal = ("recipients",)
    actions = ["start_mailing_action"]

    def start_mailing_action(self, request, queryset):
        """Action для запуска выбранных рассылок"""
        for mailing in queryset:
            result = run_mailing(mailing)
            messages.info(request, f"Рассылка #{mailing.pk}: {result}")

    start_mailing_action.short_description = "Запустить выбранные рассылки"


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("mailing", "attempt_time", "status")
    list_filter = ("status",)
