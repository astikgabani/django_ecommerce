from django.shortcuts import render, redirect
from django.http import JsonResponse

from accounts.forms import LoginForm, GuestForm
from addresses.forms import AddressForm

from addresses.models import Address
from accounts.models import GuestEmailModel
from orders.models import Order
from products.models import Product
from billing.models import BillingProfile

from .models import Cart


def cart_detail_api_view(request):
    cart_obj, status = Cart.objects.new_or_get(request)
    products = [{
                    "id": product.id,
                    "name": product.title,
                    "url": product.get_absolute_url(),
                    "price": product.price
                } for product in cart_obj.products.all()]
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)


def cart_home(request):
    cart_obj, status = Cart.objects.new_or_get(request)
    context = {
        "cart": cart_obj,
    }
    return render(request, "carts/home.html", context)


def cart_update(request):
    product_id = request.POST.get("product_id")
    if product_id:
        qs = Product.objects.filter(id=product_id)
        if qs.count() == 1:
            product_obj = qs.first()
            cart_obj, new_obj = Cart.objects.new_or_get(request)
            if product_obj in cart_obj.products.all():
                cart_obj.products.remove(product_obj)
                added = False
            else:
                cart_obj.products.add(product_obj)
                added = True
            request.session["cart_items"] = cart_obj.products.count()
            if request.is_ajax():
                json_data = {
                    "added": added,
                    "removed": not added,
                    "cartItemCount": cart_obj.products.count()
                }
                return JsonResponse(json_data)
    return redirect("cart:home")


def checkout(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    if cart_created:
        return redirect("cart:home")
    login_form = LoginForm()
    guest_form = GuestForm()
    address_form = AddressForm()

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)

    order_obj = None
    address_qs = None
    if billing_profile:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        order_obj, created = Order.objects.new_or_get(cart_obj, billing_profile)
        billing_address_id = request.session.get("billing_address_id", None)
        shipping_address_id = request.session.get("shipping_address_id", None)
        print(shipping_address_id)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session['shipping_address_id']
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session['billing_address_id']
        if shipping_address_id or billing_address_id:
            order_obj.save()

    if request.method == "POST":
        is_done = order_obj.check_done()
        if is_done:
            order_obj.mark_paid()
            request.session["cart_items"] = 0
            del request.session["cart_id"]
            return redirect("cart:success")

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs":address_qs,
    }
    return render(request, "carts/checkout.html", context)


def order_success(request):
    return render(request, "carts/order_success.html", {})
