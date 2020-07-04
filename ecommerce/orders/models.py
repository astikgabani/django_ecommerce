from math import fsum
from django.db import models
from django.db.models.signals import pre_save, post_save

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
from ecommerce.utils import unique_order_id_generator

ORDER_STATUS_CHOICES = (
    ("created", "Created"),
    ("paid", "Paid"),
    ("shipped", "Shipped"),
    ("refunded", "Refunded"),
)


class OrderManager(models.Manager):

    def new_or_get(self, cart_obj, billing_profile):
        qs = self.get_queryset().filter(cart=cart_obj, billing_profile=billing_profile, active=True, status="created")
        if qs.count() == 1:
            obj = qs.first()
            created = False
        else:
            # print(self.model.objects)
            obj = self.model.objects.create(cart=cart_obj, billing_profile=billing_profile)
            created = True
        return obj, created


class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True)
    billing_profile = models.ForeignKey(BillingProfile, models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey(Address, models.SET_NULL, related_name="shipping_address", null=True, blank=True)
    billing_address = models.ForeignKey(Address, models.SET_NULL, related_name="billing_address", null=True, blank=True)
    cart = models.ForeignKey(Cart, models.SET_NULL, null=True)
    status = models.CharField(max_length=120, default="created", choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=50.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)

    objects = OrderManager()

    def __str__(self):
        return self.order_id

    def update_total(self):
        self.total = format(fsum([self.cart.total, self.shipping_total]), ".2f")
        self.save()
        return self.total

    def check_done(self):
        if self.billing_profile and self.shipping_address and self.billing_address and self.total > 0:
            return True
        return False

    def mark_paid(self):
        if self.check_done():
            self.status = "paid"
            self.save()
        return self.status


def order_id_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    old_order_qs = Order.objects.exclude(billing_profile=instance.billing_profile).filter(cart=instance.cart, active=True)
    if old_order_qs.exists():
        old_order_qs.update(active=False)


pre_save.connect(order_id_pre_save_receiver, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
    if not created:
        cart_obj = instance
        cart_total = cart_obj.total
        cart_id = cart_obj.id
        qs = Order.objects.filter(cart__id=cart_id)
        if qs.count() == 1:
            order_obj = qs.first()
            order_obj.update_total()


post_save.connect(post_save_cart_total, sender=Cart)


def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()


post_save.connect(post_save_order, sender=Order)
