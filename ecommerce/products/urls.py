from django.contrib import admin
from django.urls import path

from .views import (
        ProductListView,
        ProductDetailView,
        ProductFeaturedListView,
        ProductFeaturedDetailView
    )

urlpatterns = [
    path('', ProductListView.as_view(), name="list"),
    path('featured/', ProductFeaturedListView.as_view()),
    path('featured/<int:pk>', ProductFeaturedDetailView.as_view()),
    path('<slug:slug>', ProductDetailView.as_view(), name="slug_view"),
]
