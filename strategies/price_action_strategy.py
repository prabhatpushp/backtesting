import pandas as pd
import numpy as np
from loguru import logger
from .base_strategy import BaseStrategy

class PriceActionStrategy(BaseStrategy):
    """
    A price action based strategy that:
    1. Buys more when price drops 10% from last buy price
    2. Sells when profit exceeds 20% from average buy price
    """
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self.validate_data(data):
            return data
        
        try:
            # Initialize variables
            data['Signal'] = 0  # 1 for buy, -1 for sell, 0 for hold
            data['Position'] = 0  # Will track our position size
            data['Avg_Buy_Price'] = 0.0  # Track average buy price
            data['Last_Buy_Price'] = 0.0  # Track last buy price
            
            position = 0  # Current position
            avg_buy_price = 0.0  # Average buy price
            last_buy_price = 0.0  # Last buy price
            
            # Process each row
            for i in range(len(data)):
                current_price = data.iloc[i]['Close']
                
                if position == 0:  # If no position, look for first buy
                    data.iloc[i, data.columns.get_loc('Signal')] = 1
                    position = 1
                    avg_buy_price = current_price
                    last_buy_price = current_price
                else:
                    # Check for additional buy condition (10% drop from last buy)
                    if current_price <= last_buy_price * 0.9:
                        data.iloc[i, data.columns.get_loc('Signal')] = 1
                        position += 1
                        # Update average buy price
                        avg_buy_price = ((avg_buy_price * (position - 1)) + current_price) / position
                        last_buy_price = current_price
                    
                    # Check for sell condition (20% profit from average)
                    elif current_price >= avg_buy_price * 1.2 and position > 0:
                        data.iloc[i, data.columns.get_loc('Signal')] = -1
                        position = 0
                        avg_buy_price = 0.0
                        last_buy_price = 0.0
                
                # Update tracking columns
                data.iloc[i, data.columns.get_loc('Position')] = position
                data.iloc[i, data.columns.get_loc('Avg_Buy_Price')] = avg_buy_price
                data.iloc[i, data.columns.get_loc('Last_Buy_Price')] = last_buy_price
            
            return data
            
        except Exception as e:
            logger.error(f"Error in PriceActionStrategy: {str(e)}")
            return data
