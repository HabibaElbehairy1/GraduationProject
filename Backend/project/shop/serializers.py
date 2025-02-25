from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import OrderItem, Product, Review, Wishlist, Cart, Order
from django.db import transaction
from django.db.models import Avg



class ProductSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()  # إضافة حقل لحساب التقييم عند الاسترجاع
    class Meta:
        model = Product
        fields = '__all__'
        lookup_field = 'slug'

    def get_rating(self, obj):
            """ إرجاع متوسط التقييم للمنتج إذا كانت هناك مراجعات، وإلا 0.0 """
            avg_rating = obj.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
            return round(avg_rating, 1) if avg_rating else 0.0


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product = serializers.StringRelatedField(read_only=True)
    product_slug = serializers.SlugField(source='product.slug', read_only=True)

    class Meta:
        model = Review
        fields = ['product_slug', 'user', 'product', 'rating', 'created_at']

    def validate(self, data):
        user = self.context['request'].user
        product_slug = self.context['view'].kwargs.get('product_slug')
        product = get_object_or_404(Product, slug=product_slug)

        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"error": "You have already reviewed this product."})

        return data

    def create(self, validated_data):
        return Review.objects.create(**validated_data)


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_slug = serializers.SlugField(write_only=True)  # إدخال `slug` بدلاً من `product`
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Wishlist
        fields = ['user', 'product', 'product_slug', 'added_at']

    def validate(self, data):
        user = self.context['request'].user
        product_slug = self.initial_data.get('product_slug')  # الحصول على `slug` من البيانات

        product = get_object_or_404(Product, slug=product_slug)  # جلب المنتج من `slug`
        
        # التحقق مما إذا كان المنتج موجودًا بالفعل في الـ Wishlist
        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"error": "This product is already in your wishlist."})

        data['product'] = product  # تعيين المنتج داخل البيانات
        return data

    def create(self, validated_data):
        validated_data.pop('product_slug')  # إزالة `slug` لأنه غير مطلوب للحفظ
        return super().create(validated_data)




class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = ['user', 'product', 'quantity', 'added_at']
        extra_kwargs = {
            'quantity': {'required': True, 'min_value': 1},  # جعل `quantity` مطلوبًا وأدنى قيمة هي 1
        }

    def validate_quantity(self, value):
        """تأكد من أن الكمية أكبر من الصفر"""
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
    def validate(self, data):
        if Cart.objects.filter(user=self.context['request'].user, product=data['product']).exists():
            raise serializers.ValidationError({"error": "This product is already in your cart."})
        return data


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.SlugField(source='product.slug', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'product_name', 'product_slug', 'quantity', 'price']
        read_only_fields = ['product_name', 'product_slug']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Order
        fields = ['user', 'phone', 'email', 'address', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['user', 'total_price', 'status', 'created_at']

    def validate(self, data):
        if not Cart.objects.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError({"error": "Cart is empty."})
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():
            order = Order.objects.create(total_price=total_price, **validated_data)

            order_items = []
            for item in cart_items:
                product = item.product
                
                if product.quantity < item.quantity:
                    raise serializers.ValidationError({"error": f"Not enough stock for {product.name}"})

                product.quantity -= item.quantity
                product.save()

                order_items.append(OrderItem(order=order, product=product, quantity=item.quantity, price=product.price))

            OrderItem.objects.bulk_create(order_items)
            cart_items.delete()

        return order
