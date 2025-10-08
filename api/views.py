from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Product
from .serializers import ProductSerializer

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# API endpoint để lấy thông tin health check
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'message': 'Django API is running! Version 11.0 - Live Manifest with PAT Token!'
    })
