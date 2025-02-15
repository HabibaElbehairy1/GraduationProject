from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductsFilter
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status

@api_view(['GET']) 
def get_by_id_product(request, pk):
    product = get_object_or_404(Product, id = pk) 
    serializer = ProductSerializer(product, many=False)
    return Response({"product": serializer.data})


@api_view(['GET']) 
def get_all_products(request):
    filterset = ProductsFilter(request.GET, queryset=Product.objects.all().order_by('id'))

    if not filterset.is_valid():
        return Response({"error": "Invalid filter parameters"}, status=400)

    serializer = ProductSerializer(filterset.qs, many=True)
    return Response({"products": serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])#,IsAdminUser])
def new_product(request):
    data = request.data
    serializer = ProductSerializer(data = data)

    if serializer.is_valid():
        product = Product.objects.create(**data,user=request.user)
        res = ProductSerializer(product,many=False)
 
        return Response({"product":res.data})
    else:
        return Response(serializer.errors)
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request,pk):
    product = get_object_or_404(Product,id=pk)

    if product.user != request.user:
        return Response({"error":"Sorry you can not update this product"}
                        , status=status.HTTP_403_FORBIDDEN)
    
    product.name = request.data.get('name', product.name)
    product.description = request.data.get('description', product.description)
    product.price = request.data.get('price', product.price)
    product.Care_Guide = request.data.get('Care_Guide', product.Care_Guide)
    product.quantity = request.data.get('quantity', product.quantity)
    product.category = request.data.get('category', product.category)

    # Update image if provided
    if 'image' in request.FILES:
        product.image = request.FILES['image']

    product.save()
    serializer = ProductSerializer(product,many=False)
    return Response({"product":serializer.data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request,pk):
    product = get_object_or_404(Product,id=pk)

    if product.user != request.user:
        return Response({"error":"Sorry you can not update this product"}
                        , status=status.HTTP_403_FORBIDDEN)

    product.delete() 
    return Response({"details":"Delete action is done"},status=status.HTTP_200_OK)