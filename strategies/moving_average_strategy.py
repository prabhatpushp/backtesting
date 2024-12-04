import pandas as pd
import talib
from loguru import logger
from .base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    """
    A simple moving average crossover strategy with RSI filter.
    Generates buy signals when:
    1. Fast MA crosses above Slow MA
    2. RSI is below oversold level
    Generates sell signals when:
    1. Fast MA crosses below Slow MA
    2. RSI is above overbought level
    """
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        if not self.validate_data(data):
            return data
        
        try:
            # Get parameters from config
            fast_period = self.params.get('MA_FAST', 20)
            slow_period = self.params.get('MA_SLOW', 50)
            rsi_period = self.params.get('RSI_PERIOD', 14)
            rsi_overbought = self.params.get('RSI_OVERBOUGHT', 70)
            rsi_oversold = self.params.get('RSI_OVERSOLD', 30)
            
            # Calculate indicators
            data['MA_Fast'] = talib.SMA(data['Close'], timeperiod=fast_period)
            data['MA_Slow'] = talib.SMA(data['Close'], timeperiod=slow_period)
            data['RSI'] = talib.RSI(data['Close'], timeperiod=rsi_period)
            
            # Generate signals
            data['Signal'] = 0
            
            # Buy conditions
            buy_condition = (
                (data['MA_Fast'] > data['MA_Slow']) & 
                (data['MA_Fast'].shift(1) <= data['MA_Slow'].shift(1)) &
                (data['RSI'] < rsi_oversold)
            )
            
            # Sell conditions
            sell_condition = (
                (data['MA_Fast'] < data['MA_Slow']) & 
                (data['MA_Fast'].shift(1) >= data['MA_Slow'].shift(1)) |
                (data['RSI'] > rsi_overbought)
            )
            
            data.loc[buy_condition, 'Signal'] = 1
            data.loc[sell_condition, 'Signal'] = -1
            
            logger.info(f"Generated signals using MA ({fast_period}/{slow_period}) and RSI ({rsi_period})")
            return data
            
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return data
