import pandas as pd
from typing import List, Dict, Any
from datetime import datetime


class Transformer:
    """Transform data using pandas"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data
        self.df = None
    
    def transform(self) -> pd.DataFrame:
        """
        Transform raw data into clean DataFrame
        
        Returns:
            Transformed pandas DataFrame
        """
        try:
            # Create DataFrame from raw data
            self.df = pd.DataFrame(self.data)
            
            # Validate required columns
            required_columns = [
                'transaction_id', 'customer_name', 'product_name',
                'category', 'quantity', 'unit_price', 'sale_date',
                'region', 'payment_method'
            ]
            
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Data type conversions
            self.df['transaction_id'] = self.df['transaction_id'].astype(str)
            self.df['customer_name'] = self.df['customer_name'].astype(str).str.strip()
            self.df['product_name'] = self.df['product_name'].astype(str).str.strip()
            self.df['category'] = self.df['category'].astype(str).str.strip()
            self.df['quantity'] = pd.to_numeric(self.df['quantity'], errors='coerce').astype(int)
            self.df['unit_price'] = pd.to_numeric(self.df['unit_price'], errors='coerce').astype(float)
            self.df['sale_date'] = pd.to_datetime(self.df['sale_date'])
            self.df['region'] = self.df['region'].astype(str).str.strip()
            self.df['payment_method'] = self.df['payment_method'].astype(str).str.strip()
            
            # Calculate total amount
            self.df['total_amount'] = (self.df['quantity'] * self.df['unit_price']).round(2)
            
            # Remove duplicates based on transaction_id
            self.df = self.df.drop_duplicates(subset=['transaction_id'])
            
            # Remove rows with null values in required columns
            self.df = self.df.dropna(subset=required_columns)
            
            # Reset index
            self.df = self.df.reset_index(drop=True)
            
            return self.df
        
        except Exception as e:
            raise Exception(f"Error transforming data: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the transformed data"""
        if self.df is None:
            raise ValueError("Data not transformed yet. Call transform() first.")
        
        return {
            'total_records': len(self.df),
            'total_amount_sum': float(self.df['total_amount'].sum()),
            'average_amount': float(self.df['total_amount'].mean()),
            'records_by_region': self.df['region'].value_counts().to_dict(),
            'records_by_category': self.df['category'].value_counts().to_dict(),
        }
