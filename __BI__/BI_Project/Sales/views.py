from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from celery.result import AsyncResult
from .models import SalesData
from .serializer import SalesDataSerializer
from .pipline import Pipeline
from .task import run_etl_pipeline
import os


class SalesDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Sales Data"""
    
    queryset = SalesData.objects.all()
    serializer_class = SalesDataSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = SalesData.objects.all()
        
        # Filter by region
        region = self.request.query_params.get('region')
        if region:
            queryset = queryset.filter(region=region)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(sale_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sale_date__lte=end_date)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-sale_date')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get sales statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_records': queryset.count(),
            'total_amount': sum([sale.total_amount for sale in queryset]),
            'average_amount': queryset.values('total_amount').count() and sum([sale.total_amount for sale in queryset]) / queryset.count() or 0,
            'by_region': {},
            'by_category': {},
        }
        
        # Statistics by region
        for record in queryset.values('region').distinct():
            region = record['region']
            region_sales = queryset.filter(region=region)
            stats['by_region'][region] = {
                'count': region_sales.count(),
                'total': sum([s.total_amount for s in region_sales])
            }
        
        # Statistics by category
        for record in queryset.values('category').distinct():
            category = record['category']
            category_sales = queryset.filter(category=category)
            stats['by_category'][category] = {
                'count': category_sales.count(),
                'total': sum([s.total_amount for s in category_sales])
            }
        
        return Response(stats)


class ETLPipelineAPIView(APIView):
    """API Endpoints for ETL Pipeline execution"""
    
    @action(detail=False, methods=['post'])
    def post(self, request):
        """
        Execute ETL pipeline manually
        
        Request body:
        {
            "json_file_path": "path/to/json/file.json" (optional, defaults to sales_data.json)
        }
        """
        try:
            json_file = request.data.get("json_file_path")
            
            # Default to Sales_Data.json in project root
            if not json_file:
                json_file = os.path.join(settings.BASE_DIR, 'Sales_Data.json')
            
            if not os.path.exists(json_file):
                return Response(
                    {'error': f'File not found: {json_file}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Execute pipeline
            pipeline = Pipeline(json_file)
            result = pipeline.run()
            
            return Response({
                'message': 'ETL Pipeline executed successfully',
                'data': result
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ETLPipelineAsyncAPIView(APIView):
    """API Endpoints for async ETL Pipeline execution using Celery"""
    
    def post(self, request):
        """
        Execute ETL pipeline asynchronously using Celery
        
        Request body:
        {
            "json_file_path": "path/to/json/file.json" (optional, defaults to sales_data.json)
        }
        """
        try:
            json_file = request.data.get('json_file_path')
            
            # Default to Sales_Data.json in project root
            if not json_file:
                json_file = os.path.join(settings.BASE_DIR, 'Sales_Data.json')
            print(f"Received request to execute ETL Pipeline for file: {json_file}")
            if not os.path.exists(json_file):
                return Response(
                    {'error': f'File not found: {json_file}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            print(f"Queueing ETL Pipeline for file: {json_file}")
            # Queue the task
            task = run_etl_pipeline.delay(json_file)
            print(f"ETL Pipeline task queued with ID: {task.id}")
            
            return Response({
                'message': 'ETL Pipeline queued for processing',
                'task_id': task.id
            }, status=status.HTTP_202_ACCEPTED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def get(self, request, task_id=None):
        """Check task status"""
        # Get task_id from URL kwargs if not provided in parameters
        if not task_id:
            task_id = self.kwargs.get('task_id')
        
        if not task_id:
            return Response(
                {'error': 'Task ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            task = AsyncResult(task_id)
            
            if task.state == 'PENDING':
                response = {'status': 'pending'}
            elif task.state == 'SUCCESS':
                response = {
                    'status': 'completed',
                    'data': task.result
                }
            elif task.state == 'FAILURE':
                response = {
                    'status': 'failed',
                    'error': str(task.info)
                }
            else:
                response = {'status': task.state}
            
            return Response(response)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

