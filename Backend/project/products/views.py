from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductsFilter


@api_view(['GET']) 
def get_by_id_product(request, pk):
    product = get_object_or_404(Product, id=pk) 
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


@api_view(['GET']) 
def get_all_products(request):
    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))

    if not filterset.is_valid():
        return Response({"error": "Invalid filter parameters"}, status=400)

    serializer = ProductSerializer(filterset.qs, many=True)
    return Response({"products": serializer.data})
