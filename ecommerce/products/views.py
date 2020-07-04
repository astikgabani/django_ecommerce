from django.http import Http404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import render, get_object_or_404

from .models import Product
from carts.models import Cart


class ProductListView(ListView):
    template_name = "product/products.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.all()


class ProductDetailView(DetailView):
    queryset = Product.objects.filter()
    template_name = "product/product_details.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context["cart"] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request = self.request
        slug = self.kwargs.get("slug")
        instance = get_object_or_404(Product, slug=slug, active=True )
        if not instance:
            raise Http404("Product doesn't exist.")
        return instance


class ProductFeaturedDetailView(DetailView):
    template_name = "product/featured_details.html"

    def get_queryset(self, *args, **kwargs):
        return Product.objects.features()


class ProductFeaturedListView(ListView):
    template_name = "product/products.html"

    def get_queryset(self, *args, **kwargs):
        return Product.objects.features()
