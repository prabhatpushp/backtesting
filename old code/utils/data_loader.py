import os
import pandas as pd
from loguru import logger
from typing import Dict, List
from config import TEST_DATA_DIR

class DataLoader:
    """Utility class for loading and preprocessing stock data."""
    
    @staticmethod
    def load_stock_data(file_path: str) -> pd.DataFrame:
        """
        Load stock data from a CSV file.
        
        Args:
            file_path (str): Path to the CSV file
            
        Returns:
            pd.DataFrame: Loaded and preprocessed stock data
        """
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns in {file_path}")
                return None
            
            # Convert Date to datetime
            df['Date'] = pd.to_datetime(df['Date'], unit="s")
            df.set_index('Date', inplace=True)
            
            # Sort by date
            df.sort_index(inplace=True)
            
            # Remove any rows with NaN values
            df.dropna(inplace=True)
            
            logger.info(f"Successfully loaded data from {os.path.basename(file_path)}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def load_all_stocks() -> Dict[str, pd.DataFrame]:
        """
        Load all stock data from the test data directory.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary mapping stock symbols to their data
        """
        stock_data = {}
        
        try:
            files = [f for f in os.listdir(TEST_DATA_DIR) if f.endswith('.csv')]
            logger.info(f"Found {len(files)} stock data files")
            
            for file in files:
                symbol = os.path.splitext(file)[0]
                file_path = os.path.join(TEST_DATA_DIR, file)
                data = DataLoader.load_stock_data(file_path)
                
                if data is not None:
                    stock_data[symbol] = data
            
            logger.info(f"Successfully loaded {len(stock_data)} stocks")
            return stock_data
            
        except Exception as e:
            logger.error(f"Error loading stock data: {str(e)}")
            return stock_data
