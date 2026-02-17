from django.db import models


class SalesData(models.Model):
    """Model to store sales data extracted, transformed, and loaded from JSON"""
    
    transaction_id = models.CharField(max_length=100, unique=True)
    customer_name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    sale_date = models.DateField()
    region = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sales_data'
        verbose_name_plural = 'Sales Data'
        indexes = [
            models.Index(fields=['sale_date']),
            models.Index(fields=['region']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.transaction_id} - {self.customer_name}"
