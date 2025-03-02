from backtesting import Strategy
from backtesting.lib import crossover
import talib as ta
import json
from datetime import datetime

class SMACross(Strategy):
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        with open("config.json", "r") as f:
            self.config = json.load(f)
    
    def init(self):
        # Get parameters from config
        short_window = self.config.get('short_window', 10)
        long_window = self.config.get('long_window', 20)
        
        # Calculate moving averages
        self.sma1 = self.I(ta.SMA, self.data.Close, timeperiod=short_window)
        self.sma2 = self.I(ta.SMA, self.data.Close, timeperiod=long_window)
    
    def next(self):
        # If we don't have any position and shorter SMA crosses above longer SMA, enter long position
        if not self.position and crossover(self.sma1, self.sma2):
            # Calculate position size based on available equity
            size = self.equity / self.data.Close[-1]
            self.buy(size=size)
        
        # If we have a position and shorter SMA crosses below longer SMA, exit position
        elif self.position and crossover(self.sma2, self.sma1):
            self.position.close()
    
    def to_dict(self):
        """Convert strategy results to JSON-serializable format"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif hasattr(value, 'to_dict'):
                result[key] = value.to_dict()
            else:
                result[key] = str(value)
        return result