from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import RegisterForm


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # автоматический вход
        return redirect("home")
