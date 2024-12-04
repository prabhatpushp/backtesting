from strategies.base_strategy import BaseStrategy
import pandas as pd

class BuyAndHoldStrategy(BaseStrategy):
    """Simple buy and hold strategy that buys at the start and holds until the end."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy and hold signals - buy at start, hold till end.
        
        Args:
            data (pd.DataFrame): OHLCV data
            
        Returns:
            pd.DataFrame: Data with added signal column
        """
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
        
        # Initialize signals column with zeros
        data['Signal'] = 0
        
        # Set buy signal (1) at the first row
        data.iloc[0, data.columns.get_loc('Signal')] = 1
        
        return data
