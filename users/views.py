from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.contrib.auth import login
from django.shortcuts import redirect

from .forms import RegisterForm


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/register.html"

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)  # автоматический вход
        return redirect("home")
