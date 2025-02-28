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
from .permissions import IsAuthenticatedWithJWT
# Base View to enforce authentication

class ProductViewSet(IsAuthenticatedWithJWT, viewsets.ModelViewSet):
    """ViewSet to manage products"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductsFilter  


class ReviewCreateView(IsAuthenticatedWithJWT, generics.CreateAPIView):
    serializer_class = ReviewSerializer
    def perform_create(self, serializer):
        product = get_object_or_404(Product, slug=self.kwargs['product_slug'])
        serializer.save(user=self.request.user, product=product)
        product.update_rating()


class ProductDetailView(IsAuthenticatedWithJWT, RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


class WishlistListCreateView(IsAuthenticatedWithJWT, generics.ListCreateAPIView):
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        product = get_object_or_404(Product, slug=self.request.data.get('product_slug'))

        if Wishlist.objects.filter(user=user, product=product).exists():
            raise ValidationError({"error": "This product is already in your wishlist."})

        serializer.save(user=user, product=product)


class WishlistDeleteView(IsAuthenticatedWithJWT, DestroyAPIView):
    serializer_class = WishlistSerializer

    def get_object(self):
        """يجلب عنصر الـ Wishlist للمستخدم بناءً على `product_slug`."""
        product = get_object_or_404(Product, slug=self.kwargs['product_slug'])
        return get_object_or_404(Wishlist, user=self.request.user, product=product)

    def delete(self, request, *args, **kwargs):
        """يحذف العنصر من Wishlist ويعيد رسالة نجاح."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Item removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)

class CartListCreateView(IsAuthenticatedWithJWT, generics.ListCreateAPIView):
    serializer_class = CartSerializer

    def get_queryset(self):
        """إرجاع جميع المنتجات التي تمت إضافتها في `Cart` بواسطة المستخدم الحالي."""
        return Cart.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """إضافة منتج إلى `Cart` أو تحديث الكمية إذا كان موجودًا بالفعل."""
        user = request.user
        product_slug = request.data.get('product_slug')

        # التحقق من وجود `product_slug` في الطلب
        if not product_slug:
            return Response({"error": "Product slug is required."}, status=status.HTTP_400_BAD_REQUEST)

        # جلب المنتج أو إرجاع خطأ 404 إذا لم يكن موجودًا
        product = get_object_or_404(Product, slug=product_slug)

        # التحقق من المخزون قبل الإضافة إلى السلة
        cart_item, created = Cart.objects.get_or_create(user=user, product=product, defaults={'quantity': 1})

        if not created:
            if cart_item.quantity >= product.quantity:
                return Response(
                    {"error": f"Only {product.quantity} items available in stock."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity += 1
            cart_item.save()
            return Response(
                {"message": "Quantity updated.", "cart_item": CartSerializer(cart_item).data},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(cart_item)
        return Response(
            {"message": "Product added to cart.", "cart_item": serializer.data},
            status=status.HTTP_201_CREATED
        )


class CartUpdateDeleteView(IsAuthenticatedWithJWT, UpdateAPIView, DestroyAPIView):
    serializer_class = CartSerializer

    def get_object(self):
        """استرجاع العنصر المطلوب تعديله أو حذفه من `Cart`"""
        product = get_object_or_404(Product, slug=self.kwargs['product_slug'])
        return get_object_or_404(Cart, user=self.request.user, product=product)

    def update(self, request, *args, **kwargs):
        """تقليل الكمية بمقدار 1 أو حذف العنصر إذا كانت الكمية 1."""
        cart_item = self.get_object()

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            return Response(
                {"message": "Item quantity reduced by 1.", "cart_item": CartSerializer(cart_item).data},
                status=status.HTTP_200_OK
            )
        

        # حذف العنصر مباشرة بدلاً من رفض التعديل
        cart_item.delete()
        return Response(
            {"message": "Item removed from cart as quantity reached 0."},
            status=status.HTTP_204_NO_CONTENT
        )


class CheckoutView(IsAuthenticatedWithJWT, generics.CreateAPIView):
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        phone = request.data.get('phone')
        email = request.data.get('email')
        address = request.data.get('address')

        if not all([phone, email, address]):
            raise ValidationError({"error": "Phone, email, and address are required."})

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError({"error": "Cart is empty. Add items before checkout."})

        order_data = {"user": user.id, "phone": phone, "email": email, "address": address}

        with transaction.atomic():
            serializer = self.get_serializer(data=order_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()

        return Response(
            {"message": "Order placed successfully!", "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED
        )


class OrderListView(IsAuthenticatedWithJWT, generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
