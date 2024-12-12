from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductsFilter

# Get a product by its ID
@api_view(['GET']) 
def get_by_id_product(request, pk):
    product = get_object_or_404(Product, id=pk)  # Ensure you're fetching the product correctly
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})

# Get all products with filtering options
@api_view(['GET']) 
def get_all_products(request):
    # Applying filters
    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))
    
    # You can check if filterset is valid
    if not filterset.is_valid():
        return Response({"error": "Invalid filter parameters"}, status=400)

    # Serialize the filtered products
    serializer = ProductSerializer(filterset.qs, many=True)
    return Response({"products": serializer.data})
