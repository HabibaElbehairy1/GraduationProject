
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, ProductDetailView, ReviewCreateView, WishlistListCreateView, 
    WishlistDeleteView, CartListCreateView, CartUpdateDeleteView, CheckoutView, OrderListView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),  # البحث عبر slug
    path('products/<slug:product_slug>/rate/', ReviewCreateView.as_view(), name='add-review'),  # تعديل الربط بـ slug
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist'),
    path('wishlist/delete/<slug:product_slug>/', WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('cart/', CartListCreateView.as_view(), name='cart'),
    path('cart/reduce-delete/<slug:product_slug>/', CartUpdateDeleteView.as_view(), name='cart-reduce'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),
]
