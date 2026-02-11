from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
from .models import Mailing, Recipient, MailingAttempt

@login_required
def home(request):
    now = timezone.now()

    # Все рассылки пользователя
    user_mailings = Mailing.objects.filter(owner=request.user)
    total_mailings = user_mailings.count()

    active_mailings = user_mailings.filter(
        start_time__lte=now,
        end_time__gte=now,
        status=Mailing.STATUS_STARTED
    ).count()

    unique_recipients = Recipient.objects.filter(
        owner=request.user
    ).count()

    # --- СТАТИСТИКА ПО ПОПЫТКАМ ---
    attempts = MailingAttempt.objects.filter(
        mailing__owner=request.user
    )

    success_attempts = attempts.filter(
        status=MailingAttempt.STATUS_SUCCESS
    ).count()

    failed_attempts = attempts.filter(
        status=MailingAttempt.STATUS_FAILED
    ).count()

    total_attempts = attempts.count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
        "success_attempts": success_attempts,
        "failed_attempts": failed_attempts,
        "total_attempts": total_attempts,
    }

    return render(request, "mailing/home.html", context)
