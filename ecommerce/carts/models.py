from django.db import models
from django.conf import settings

from django.db.models.signals import pre_save, m2m_changed

User = settings.AUTH_USER_MODEL

from products.models import Product


class CartManager(models.Manager):

    def new_or_get(self, request):
        cart_id = request.session.get("cart_id", None)
        qs = self.get_queryset().filter(id=cart_id)
        if qs.count() == 1:
            new_cart = False
            cart_obj = qs.first()
            if request.user.is_authenticated and cart_obj.user is None:
                cart_obj.user = request.user
                cart_obj.save()
        else:
            new_cart = True
            cart_obj = self.new(user=request.user)
            request.session["cart_id"] = cart_obj.id
        return cart_obj, new_cart

    def new(self, user):
        user_obj = None
        if user is not None:
            if user.is_authenticated:
                user_obj = user
        return self.model.objects.create(user=user_obj)


class Cart(models.Model):
    user = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=True)
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)


def cart_m2m_changed_receiver(sender, instance, action, *args, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        products = instance.products.all()
        subtotal = 0
        for x in products:
            subtotal += x.price
        instance.subtotal = subtotal
        instance.save()


m2m_changed.connect(cart_m2m_changed_receiver, sender=Cart.products.through)


def cart_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.subtotal > 0:
        instance.total = instance.subtotal
    else:
        instance.total = 0.00


pre_save.connect(cart_pre_save_receiver, sender=Cart)
