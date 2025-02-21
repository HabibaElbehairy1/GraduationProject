from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import OrderItem, Product, Review, Wishlist, Cart, Order
from django.db import transaction 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [field.name for field in Product._meta.fields if field.name != "id"]
        lookup_field = 'slug'



class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Show username instead of ID
    product = serializers.StringRelatedField(read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True) 
    class Meta:
        model = Review
        fields = ['product_slug', 'user', 'product', 'rating', 'created_at']

 
    def create(self, validated_data):
        user = self.context['request'].user
        product_slug = self.context['view'].kwargs.get('product_slug')  # استخدم get() لتجنب الأخطاء

        product = Product.objects.get(slug=product_slug)  


        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError({"error": "You have already reviewed this product."})

        review = Review.objects.create(user=user, product=product, **validated_data)

        product.update_rating()

        return review



class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  

    class Meta:
        model = Wishlist
        fields = [ 'product', 'added_at']  

    def create(self, validated_data):
        return Wishlist.objects.create(**validated_data)



class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    

    class Meta:
        model = Cart
        fields = [ 'product','quantity', 'added_at',]

    def create(self, validated_data):
 
        return Cart.objects.create( **validated_data)



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'product_slug', 'quantity', 'price']
        read_only_fields = ['id', 'product_name', 'product_slug']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'phone', 'email', 'address', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['user', 'total_price', 'status', 'created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError({"error": "Cart is empty."})

     
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        with transaction.atomic():
 
            order = Order.objects.create(user=user, total_price=total_price, **validated_data)

         
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

