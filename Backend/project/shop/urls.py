
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (

    CartUpdateDeleteView,
    CheckoutView,
    OrderListView,
    ProductDetailView,
    ProductViewSet,
    ReviewCreateView,
    WishlistListCreateView,
    WishlistDeleteView,
    CartListCreateView
)

# Using DefaultRouter for ProductViewSet
router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    # product , filter , review
    path('', include(router.urls)),  
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'), 
    path('products/<slug:product_slug>/rate/', ReviewCreateView.as_view(), name='add-review'),

    # Wishlist
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist'),
    path('wishlist/delete/<slug:slug>/', WishlistDeleteView.as_view(), name='wishlist-delete'), 
    
    # Cart
    path('cart/', CartListCreateView.as_view(), name='cart'),
    path('cart/reduce-delete/<slug:slug>/', CartUpdateDeleteView.as_view(), name='cart-reduce'),  
    
    # Checkout & Orders
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', OrderListView.as_view(), name='order-list'),



]
