from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .forms import LoginForm, RegisterForm, GuestForm
from .models import GuestEmailModel


def login_guest_view(request):
    form = GuestForm(request.POST or None)
    context = {
        "form": form
    }
    redirect_path = request.GET.get("next") or request.POST.get("next") or None
    if form.is_valid():
        email = form.cleaned_data.get("email")
        new_guest_email_obj = GuestEmailModel.objects.create(email=email)
        request.session['guest_email_id'] = new_guest_email_obj.id
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)

        return redirect("/register/")


def login_page(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form
    }
    print(request.user.is_authenticated)
    redirect_path = request.GET.get("next") or request.POST.get("next") or None
    if form.is_valid():
        form_data = form.cleaned_data
        context["form"] = LoginForm()
        user = authenticate(**form_data)
        if user:
            try:
                del request.session["guest_email_id"]
            except:
                pass
            login(request, user)
            if is_safe_url(redirect_path, request.get_host()):
                return redirect(redirect_path)
            else:
                return redirect("/")
        else:
            print("Error")

    return render(request, "auth/login.html", context)


def register_page(request):
    form = RegisterForm(request.POST or None)
    context = {
        "form": form
    }
    if form.is_valid():
        form_data = form.cleaned_data
        new_user = User.objects.create_user(**form_data)
    return render(request, "auth/register.html", context)
