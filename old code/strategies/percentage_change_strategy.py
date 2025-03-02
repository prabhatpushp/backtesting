import pandas as pd
import numpy as np
from loguru import logger
from .base_strategy import BaseStrategy

class PercentageChangeStrategy(BaseStrategy):
    """
    A strategy that:
    1. Buys stocks proportional to the percentage drop in price
    2. Sells stocks proportional to the percentage rise in price (only if profitable)
    """
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self.validate_data(data):
            return data
        
        try:
            # Initialize variables
            data['Signal'] = 0  # 1 for buy, -1 for sell, 0 for hold
            data['Position'] = 0  # Will track our position size
            data['Avg_Buy_Price'] = 0.0  # Track average buy price
            data['Shares_Owned'] = 0  # Track number of shares owned
            
            position = 0  # Current position
            avg_buy_price = 0.0  # Average buy price
            shares_owned = 0  # Number of shares currently owned
            max_position = 100  # Maximum percentage of capital to use
            min_price_change = 0.01  # Minimum 1% change required for action
            
            # Process each row
            for i in range(1, len(data)):
                current_price = data.iloc[i]['Close']
                prev_price = data.iloc[i-1]['Close']
                
                # Calculate percentage change
                price_change_pct = (current_price - prev_price) / prev_price
                
                # If price dropped
                if price_change_pct < -min_price_change:
                    # Buy shares proportional to the drop
                    drop_pct = abs(price_change_pct)
                    shares_to_buy = int((drop_pct * max_position))
                    
                    if shares_to_buy > 0:
                        # Update position and average buy price
                        new_shares = shares_owned + shares_to_buy
                        avg_buy_price = ((shares_owned * avg_buy_price) + 
                                       (shares_to_buy * current_price)) / new_shares
                        shares_owned = new_shares
                        data.iloc[i, data.columns.get_loc('Signal')] = 1
                        data.iloc[i, data.columns.get_loc('Shares_Owned')] = shares_owned
                        data.iloc[i, data.columns.get_loc('Avg_Buy_Price')] = avg_buy_price
                
                # If price rose and we have shares
                elif price_change_pct > min_price_change and shares_owned > 0:
                    # Only sell if profitable
                    if current_price > avg_buy_price:
                        # Sell shares proportional to the rise
                        rise_pct = price_change_pct
                        shares_to_sell = int(min(shares_owned, rise_pct * shares_owned))
                        
                        if shares_to_sell > 0:
                            shares_owned -= shares_to_sell
                            data.iloc[i, data.columns.get_loc('Signal')] = -1
                            data.iloc[i, data.columns.get_loc('Shares_Owned')] = shares_owned
                            # Keep avg_buy_price same as we're selling
                            data.iloc[i, data.columns.get_loc('Avg_Buy_Price')] = avg_buy_price
                
                # Update position tracking
                data.iloc[i, data.columns.get_loc('Position')] = shares_owned
            
            return data
            
        except Exception as e:
            logger.error(f"Error in PercentageChangeStrategy: {str(e)}")
            return data
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that required columns exist in the data"""
        required_columns = ['Close']
        return all(col in data.columns for col in required_columns)
