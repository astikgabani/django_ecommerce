from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from billing.models import BillingProfile
from .models import Address
from .forms import AddressForm


def checkout_address_create_view(request):
    form = AddressForm(request.POST or None)
    context = {
        "form": form
    }
    redirect_path = request.GET.get("next") or request.POST.get("next") or None
    if form.is_valid():
        print(request.POST)
        instance = form.save(commit=False)
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if billing_profile:
            address_type = request.POST.get("address_type", "shipping")
            instance.billing_profile = billing_profile
            instance.address_type = address_type
            instance.save()

            request.session[address_type + "_address_id"] = instance.id
        else:
            print("Error Here")
            return redirect("cart:checkout")
        if is_safe_url(redirect_path, request.get_host()):
            return redirect(redirect_path)
    return redirect("cart:checkout")


def checkout_address_reuse_view(request):
    if request.user.is_authenticated:
        context = {}
        redirect_path = request.GET.get("next") or request.POST.get("next") or None
        if request.method == "POST":
            print(request.POST)
            billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
            address_type = request.POST.get("address_type", "shipping")
            shipping_address = request.POST.get("shipping_address", None)
            if shipping_address:
                qs = Address.objects.filter(billing_profile=billing_profile, id=shipping_address)
                if qs.exists():
                    request.session[address_type + "_address_id"] = shipping_address
                if is_safe_url(redirect_path, request.get_host()):
                    return redirect(redirect_path)
    return redirect("cart:checkout")
