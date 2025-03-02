import os
import json
import pandas as pd
import logging
from typing import Dict, Optional

class DataLoader:
    """
    Data loader class to handle loading and preprocessing of stock data
    """
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the data loader with configuration
        
        Args:
            config_path (str): Path to the configuration file
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Setup logging
        logging.basicConfig(
            level=self.config['logging']['level'],
            format=self.config['logging']['format']
        )
        self.logger = logging.getLogger(__name__)
        
        # Extract data configuration
        self.data_config = self.config['data']
    
    def load_stock_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load stock data from a CSV file
        
        Args:
            file_path (str): Path to the stock data file
            
        Returns:
            pd.DataFrame: Loaded and preprocessed stock data
        """
        try:
            df = pd.read_csv(file_path)
            
            # Convert date column to datetime - try different formats
            try:
                df[self.data_config['date_column']] = pd.to_datetime(df[self.data_config['date_column']], unit='s')
            except ValueError:
                df[self.data_config['date_column']] = pd.to_datetime(df[self.data_config['date_column']])
            
            df.set_index(self.data_config['date_column'], inplace=True)
            
            # Ensure all required columns are present
            required_columns = [
                self.data_config['open_column'],
                self.data_config['high_column'],
                self.data_config['low_column'],
                self.data_config['close_column'],
                self.data_config['volume_column']
            ]
            
            if not all(col in df.columns for col in required_columns):
                return None
            
            # Rename columns to standard format
            df.rename(columns={
                self.data_config['open_column']: 'Open',
                self.data_config['high_column']: 'High',
                self.data_config['low_column']: 'Low',
                self.data_config['close_column']: 'Close',
                self.data_config['volume_column']: 'Volume'
            }, inplace=True)
            
            return df
            
        except Exception as e:
            return None
    
    def load_all_stocks(self, directory: str) -> Dict[str, pd.DataFrame]:
        """
        Load all stock data from a directory
        
        Args:
            directory (str): Directory containing stock data files
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping stock symbols to their data
        """
        self.logger.info("Starting data loading process")
        stock_data = {}
        
        if not os.path.exists(directory):
            return stock_data
        
        for filename in os.listdir(directory):
            if filename.endswith(self.data_config['file_format']):
                file_path = os.path.join(directory, filename)
                symbol = os.path.splitext(filename)[0]
                
                df = self.load_stock_data(file_path)
                if df is not None:
                    stock_data[symbol] = df
        
        self.logger.info("Data loading process completed")
        return stock_data