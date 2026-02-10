from django.shortcuts import render
from django.utils import timezone

from .models import Mailing, Recipient


def home(request):
    now = timezone.now()

    total_mailings = Mailing.objects.count()

    active_mailings = Mailing.objects.filter(
        start_time__lte=now, end_time__gte=now, status=Mailing.STATUS_STARTED
    ).count()

    unique_recipients = Recipient.objects.count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
    }

    return render(request, "mailing/home.html", context)
