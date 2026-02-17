from rest_framework import serializers
from .models import SalesData


class SalesDataSerializer(serializers.ModelSerializer):
    """Serializer for SalesData model"""
    
    class Meta:
        model = SalesData
        fields = [
            'id',
            'transaction_id',
            'customer_name',
            'product_name',
            'category',
            'quantity',
            'unit_price',
            'total_amount',
            'sale_date',
            'region',
            'payment_method',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
