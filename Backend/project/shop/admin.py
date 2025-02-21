from django.contrib import admin
from .models import Order, OrderItem, Review
from django.contrib import admin

admin.site.site_header = "My Custom Admin Panel"
admin.site.site_title = "Custom Admin"
admin.site.index_title = "Welcome to the Dashboard"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'email', 'phone')
    inlines = [OrderItemInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing order
            return ('user', 'phone', 'email', 'address', 'total_price', 'created_at')
        return ()

    def has_add_permission(self, request):
        return False  # Admin cannot add new orders

admin.site.register(Order, OrderAdmin)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price')
    readonly_fields = ('order', 'product', 'quantity', 'price')

    def has_add_permission(self, request):
        return False  # Admin cannot add new order items

admin.site.register(OrderItem, OrderItemAdmin)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('user', 'product', 'created_at', 'rating')  # Admin cannot edit user/product
        return ()

    def has_add_permission(self, request):
        return False  # Admin cannot add new reviews

admin.site.register(Review, ReviewAdmin)


