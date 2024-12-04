from abc import ABC, abstractmethod
import pandas as pd
from loguru import logger

class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, params=None):
        self.params = params or {}
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals for the given data.
        
        Args:
            data (pd.DataFrame): OHLCV data with technical indicators
            
        Returns:
            pd.DataFrame: Data with added signal column
        """
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """
        Validate that the data contains required columns.
        
        Args:
            data (pd.DataFrame): Input data
            
        Returns:
            bool: True if data is valid
        """
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Missing required columns. Required: {required_columns}")
            return False
        return True
