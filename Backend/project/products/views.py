from django.shortcuts import render , get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductsFilter

# @api_view(['GET'])
# def get_all_products(request):
#     products = Product.objects.all()
#     serializer = ProductSerializer(products,many = True) 
#     print(products)
#     return Response({"products":serializer.data})   

@api_view(['GET']) 
def get_by_id_product(request , pk):
    products = get_object_or_404(Product,id=pk)
    serializer = ProductSerializer(products,many = False)
    print(products)
    return Response({"product":serializer.data}) 


@api_view(['GET']) 
def get_all_products( request ):
    # products = Product.objects.all()
    filtterset = ProductsFilter(request.GET ,queryset = Product.objects.all().order_by('id'))
    # serializer = ProductSerializer( products , many = True )
    serializer = ProductSerializer( filtterset.qs , many = True )
    # print(products)
    return Response({"products" : serializer.data})   

