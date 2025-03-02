import pandas as pd
import numpy as np
from loguru import logger
from .base_strategy import BaseStrategy

class PriceActionStrategy(BaseStrategy):
    """
    A price action based strategy that:
    1. Buys more when price drops in 5% increments from last buy price
    2. Sells portions when price rises in 5% increments from average buy price
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
            max_position = 10  # Maximum number of positions to take
            drop_threshold = 0.05  # 5% threshold for buying
            profit_threshold = 0.1  # 5% threshold for selling
            
            # Process each row
            for i in range(len(data)):
                current_price = data.iloc[i]['Close']
                
                if position == 0:  # If no position, look for first buy
                    data.iloc[i, data.columns.get_loc('Signal')] = 1
                    position = 1
                    avg_buy_price = current_price
                    last_buy_price = current_price
                else:
                    # Calculate price drop percentage from last buy
                    price_drop = (last_buy_price - current_price) / last_buy_price
                    
                    # Calculate profit percentage from average buy price
                    profit = (current_price - avg_buy_price) / avg_buy_price
                    
                    # Buy more if price drops by additional 5% increments and we haven't reached max position
                    if price_drop >= drop_threshold and position < max_position:
                        data.iloc[i, data.columns.get_loc('Signal')] = 1
                        position += 1
                        # Update average buy price
                        avg_buy_price = ((avg_buy_price * (position - 1)) + current_price) / position
                        last_buy_price = current_price
                    
                    # Sell portions if profit reaches 5% increments
                    elif profit >= profit_threshold and position > 0:
                        # Calculate how many portions to sell based on profit level
                        portions_to_sell = min(
                            position,
                            int(profit / profit_threshold)  # Sell more portions at higher profit levels
                        )
                        
                        if portions_to_sell > 0:
                            data.iloc[i, data.columns.get_loc('Signal')] = -portions_to_sell
                            position -= portions_to_sell
                            
                            # Reset prices if we sold everything
                            if position == 0:
                                avg_buy_price = 0.0
                                last_buy_price = 0.0
                
                # Update position tracking
                data.iloc[i, data.columns.get_loc('Position')] = position
                data.iloc[i, data.columns.get_loc('Avg_Buy_Price')] = avg_buy_price
                data.iloc[i, data.columns.get_loc('Last_Buy_Price')] = last_buy_price
            
            return data
            
        except Exception as e:
            logger.error(f"Error in PriceActionStrategy: {str(e)}")
            return data