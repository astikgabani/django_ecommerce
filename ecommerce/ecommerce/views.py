from django.shortcuts import render, redirect

from .forms import ContactForm


def home_page(request):
    context = {}
    return render(request, "home_page.html", context)


def about_page(request):
    context = {}
    return render(request, "about.html", context)


def contact_page(request):
    contact_form = ContactForm(request.POST or None)
    context = {"form": contact_form}
    if contact_form.is_valid():
        print(contact_form.cleaned_data)
    return render(request, "contact/contact.html", context)
