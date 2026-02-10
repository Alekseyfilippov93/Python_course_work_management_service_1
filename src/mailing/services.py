from django.core.mail import send_mail
from django.utils import timezone

from .models import Mailing, MailingAttempt


def run_mailing(mailing: Mailing):
    """
    Отправка сообщений по требованию для конкретной рассылки.
    """
    now = timezone.now()

    # Проверка временного окна
    if not (mailing.start_time <= now <= mailing.end_time):
        return f"Рассылка не активна. Текущее время: {now}"

    recipients = mailing.recipients.all()
    message = mailing.message

    for recipient in recipients:
        try:
            send_mail(
                subject=message.subject,
                message=message.body,
                from_email=None,  # используем DEFAULT_FROM_EMAIL
                recipient_list=[recipient.email],
                fail_silently=False,
            )
            # Успешная попытка
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_SUCCESS,
                server_response="Отправлено успешно",
            )
        except Exception as e:
            # Ошибка отправки
            MailingAttempt.objects.create(
                mailing=mailing,
                status=MailingAttempt.STATUS_FAILED,
                server_response=str(e),
            )

    # Обновляем статус рассылки после отправки
    mailing.update_status()
    return f"Рассылка выполнена. Отправлено {recipients.count()} писем."
