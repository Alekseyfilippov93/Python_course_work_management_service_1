from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from mailing.models import Mailing, MailingAttempt, Message, Recipient

from .services import run_mailing


# Действие для блокировки выбранных пользователей
@admin.action(description="Заблокировать выбранных пользователей")
def block_users(modeladmin, request, queryset):
    queryset.update(is_active=False)


# Сначала снимаем регистрацию User
admin.site.unregister(User)


# Кастомный UserAdmin с поддержкой блокировки
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    actions = [block_users]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Суперпользователь видит всех
        if request.user.is_superuser:
            return qs
        # Менеджер видит всех
        if request.user.groups.filter(name="Manager").exists():
            return qs
        # Обычный пользователь видит только себя
        return qs.filter(id=request.user.id)


class BaseOwnerAdmin(admin.ModelAdmin):
    exclude = ("owner",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Суперпользователь видит всё
        if request.user.is_superuser:
            return qs

        # Менеджер видит всё
        if request.user.groups.filter(name="Manager").exists():
            return qs

        # Обычный пользователь видит только свои записи
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        # Менеджер не может редактировать
        if request.user.groups.filter(name="Manager").exists():
            return False

        # Пользователь может редактировать только свои
        if obj and obj.owner != request.user:
            return False

        return True

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        # Менеджер не может удалять
        if request.user.groups.filter(name="Manager").exists():
            return False

        if obj and obj.owner != request.user:
            return False

        return True


@admin.register(Recipient)
class RecipientAdmin(BaseOwnerAdmin):
    list_display = ("email", "full_name")
    search_fields = ("email", "full_name")


@admin.register(Message)
class MessageAdmin(BaseOwnerAdmin):
    list_display = ("subject",)
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(BaseOwnerAdmin):
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

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.groups.filter(name="Manager").exists():
            return qs

        return qs.filter(mailing__owner=request.user)
