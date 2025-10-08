from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Product
from .serializers import ProductSerializer
import logging
import time

# Setup logging
logger = logging.getLogger(__name__)

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get(self, request, *args, **kwargs):
        logger.info(f"📋 GET /api/products/ - Request từ {request.META.get('REMOTE_ADDR', 'unknown')}")
        logger.info(f"📋 User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}")
        
        try:
            products = Product.objects.all()
            logger.info(f"📋 Tìm thấy {products.count()} sản phẩm trong database")
            
            response = super().get(request, *args, **kwargs)
            logger.info(f"📋 Response: {response.status_code} - Trả về {len(response.data)} sản phẩm")
            return response
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi lấy danh sách sản phẩm: {str(e)}")
            raise
    
    def post(self, request, *args, **kwargs):
        logger.info(f"➕ POST /api/products/ - Tạo sản phẩm mới từ {request.META.get('REMOTE_ADDR', 'unknown')}")
        logger.info(f"➕ Data: {request.data}")
        
        response = super().post(request, *args, **kwargs)
        logger.info(f"➕ Tạo sản phẩm thành công: {response.status_code}")
        return response

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        logger.info(f"🔍 GET /api/products/{product_id}/ - Xem chi tiết sản phẩm")
        
        response = super().get(request, *args, **kwargs)
        logger.info(f"🔍 Response: {response.status_code}")
        return response

# API endpoint để lấy thông tin health check
def health_check(request):
    logger.info(f"💚 GET /api/health/ - Health check từ {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    return JsonResponse({
        'status': 'healthy',
        'message': 'Django API is running! Version 21.0 - ARGOCD IMAGE UPDATER!',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'pod_info': 'Logs đã được enable - Xem trong ArgoCD UI!'
    })
