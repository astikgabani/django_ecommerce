from django.contrib import admin
from django.urls import path

from .views import (
        cart_home,
        cart_update,
        checkout,
        order_success,
    )

urlpatterns = [
    path('', cart_home, name="home"),
    path('checkout/', checkout, name="checkout"),
    path('update/', cart_update, name="update"),
    path('success/', order_success, name="success"),
]
