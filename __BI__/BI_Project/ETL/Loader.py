import pandas as pd
from django.db import transaction
import os
import sys
import django

# Add parent directory to path for Django imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Sales.models import SalesData
from django.core.exceptions import ValidationError
from typing import Dict, Any


class Loader:
    """Load transformed data into PostgreSQL database"""
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe
        self.loaded_count = 0
        self.failed_count = 0
        self.errors = []
    
    def load(self) -> Dict[str, Any]:
        """
        Load data into SalesData model
        
        Returns:
            Dictionary with loading statistics
        """
        try:
            with transaction.atomic():
                for idx, row in self.df.iterrows():
                    try:
                        # Check if record already exists
                        existing = SalesData.objects.filter(
                            transaction_id=row['transaction_id']
                        ).first()
                        
                        if existing:
                            # Update existing record
                            existing.customer_name = row['customer_name']
                            existing.product_name = row['product_name']
                            existing.category = row['category']
                            existing.quantity = int(row['quantity'])
                            existing.unit_price = float(row['unit_price'])
                            existing.total_amount = float(row['total_amount'])
                            existing.sale_date = row['sale_date'].date()
                            existing.region = row['region']
                            existing.payment_method = row['payment_method']
                            existing.save()
                        else:
                            # Create new record
                            SalesData.objects.create(
                                transaction_id=row['transaction_id'],
                                customer_name=row['customer_name'],
                                product_name=row['product_name'],
                                category=row['category'],
                                quantity=int(row['quantity']),
                                unit_price=float(row['unit_price']),
                                total_amount=float(row['total_amount']),
                                sale_date=row['sale_date'].date(),
                                region=row['region'],
                                payment_method=row['payment_method'],
                            )
                        
                        self.loaded_count += 1
                    
                    except Exception as e:
                        self.failed_count += 1
                        self.errors.append({
                            'row': idx,
                            'transaction_id': row.get('transaction_id', 'N/A'),
                            'error': str(e)
                        })
            
            return self.get_status()
        
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get loader execution status"""
        return {
            'loaded_count': self.loaded_count,
            'failed_count': self.failed_count,
            'total_records': self.loaded_count + self.failed_count,
            'errors': self.errors if self.errors else None
        }
    