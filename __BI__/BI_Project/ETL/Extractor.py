import json
from typing import List, Dict, Any
import os


class Extractor:
    """Extract data from JSON file"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def extract(self) -> List[Dict[str, Any]]:
        """
        Extract data from JSON file
        
        Returns:
            List of dictionaries containing extracted data
        """
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")
            
            with open(self.file_path, 'r') as file:
                data = json.load(file)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                return [data]
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
        except Exception as e:
            raise Exception(f"Error extracting data: {str(e)}")
