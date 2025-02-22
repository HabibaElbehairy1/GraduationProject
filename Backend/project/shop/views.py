import django_filters
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import DestroyAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, Order, Product, Review, Wishlist
from .serializers import CartSerializer, OrderSerializer, ProductSerializer, ReviewSerializer, WishlistSerializer
from .filters import ProductsFilter  

# Base View to enforce authentication
class AuthenticatedView:
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class ProductViewSet(AuthenticatedView, viewsets.ModelViewSet):
    """ViewSet to manage products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductsFilter  


class ReviewCreateView(AuthenticatedView, generics.CreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product_slug = self.kwargs['product_slug']
        product = get_object_or_404(Product, slug=product_slug)
        serializer.save(product=product)
        product.update_rating()


class ProductDetailView(AuthenticatedView, RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class WishlistListCreateView(AuthenticatedView, generics.ListCreateAPIView):
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product_slug = self.request.data.get('product')

        product = get_object_or_404(Product, slug=product_slug)

        if Wishlist.objects.filter(user=user, product=product).exists():
            raise ValidationError({"error": "This product is already in your wishlist."})

        serializer.save(user=user, product=product)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Item added to wishlist.", "wishlist_item": response.data},
            status=status.HTTP_201_CREATED
        )


class WishlistDeleteView(AuthenticatedView, DestroyAPIView):
    serializer_class = WishlistSerializer
    queryset = Wishlist.objects.all()

    def get_object(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        return get_object_or_404(Wishlist, user=self.request.user, product=product)

    def destroy(self, request, *args, **kwargs):
        wishlist_item = self.get_object()
        self.perform_destroy(wishlist_item)
        return Response({"message": "Item removed from wishlist."}, status=status.HTTP_200_OK)


class CartListCreateView(AuthenticatedView, generics.ListCreateAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product_slug = self.request.data.get('product')
        product = get_object_or_404(Product, slug=product_slug)

        cart_item = Cart.objects.filter(user=user, product=product).first()

        if cart_item:
            cart_item.quantity += 1
            cart_item.save()
            raise ValidationError({"message": "Quantity updated.", "cart_item": CartSerializer(cart_item).data})

        serializer.save(user=user, product=product)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Item added to cart.", "cart_item": response.data},
            status=status.HTTP_201_CREATED
        )


class CartUpdateDeleteView(AuthenticatedView, UpdateAPIView, DestroyAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        product = get_object_or_404(Product, slug=self.kwargs['slug'])
        return get_object_or_404(Cart, user=self.request.user, product=product)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return Response(
                {"message": "Item quantity reduced by 1.", "cart_item": CartSerializer(cart_item).data},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": "Cannot reduce quantity below 1. Use DELETE API instead."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart."},
            status=status.HTTP_200_OK
        )


class CheckoutView(AuthenticatedView, generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        phone = request.data.get('phone')
        email = request.data.get('email')
        address = request.data.get('address')

        if not (phone and email and address):
            raise ValidationError({"error": "Phone, email, and address are required."})

        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise ValidationError({"error": "Cart is empty. Add items before checkout."})

        order_data = {
            "user": user.id,
            "phone": phone,
            "email": email,
            "address": address
        }

        with transaction.atomic():
            serializer = self.get_serializer(data=order_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()

        return Response(
            {"message": "Order placed successfully!", "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED
        )


class OrderListView(AuthenticatedView, generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
