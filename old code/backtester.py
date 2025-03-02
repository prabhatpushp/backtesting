from backtesting import Backtest, Strategy
import pandas as pd
from loguru import logger
import os
from typing import Dict, Any
from config import INITIAL_CASH, COMMISSION, RESULTS_DIR

class BacktestEngine:
    """Main backtesting engine that runs strategies on stock data."""
    
    def __init__(self, data: pd.DataFrame, strategy_instance: Strategy, 
                 stock_symbol: str, params: Dict[str, Any] = None):
        self.data = data
        self.strategy = strategy_instance
        self.symbol = stock_symbol
        self.params = params or {}
        
    def run(self, plot: bool = False) -> Dict[str, Any]:
        """
        Run the backtest for a single stock.
        
        Args:
            plot (bool): Whether to plot the backtest results
        
        Returns:
            Dict[str, Any]: Dictionary containing backtest results
        """
        try:
            # Generate trading signals
            data_with_signals = self.strategy.generate_signals(self.data.copy())
            signals = data_with_signals['Signal'].values  # Convert to numpy array
            
            # Create a custom strategy class for backtesting library
            class CustomStrategy(Strategy):
                def init(self):
                    # Create signal indicator array
                    self.signals = signals
                    self.signal_index = 0
                
                def next(self):
                    if self.signal_index < len(self.signals):
                        current_signal = self.signals[self.signal_index]
                        
                        if current_signal == 1 and not self.position:
                            self.buy()
                        elif current_signal == -1 and self.position:
                            self.position.close()
                            
                        self.signal_index += 1
            
            # Initialize and run backtest
            self.bt = Backtest(
                data_with_signals,
                CustomStrategy,
                cash=INITIAL_CASH,
                commission=COMMISSION
            )
            
            stats = self.bt.run()
            
            if plot:
                self.bt.plot(filename=os.path.join(RESULTS_DIR, f"{self.symbol}_backtest.html"))
            
            return {
                'symbol': self.symbol,
                'return': float(stats['Return [%]']),
                'sharpe': float(stats['Sharpe Ratio']),
                'max_drawdown': float(stats['Max. Drawdown [%]']),
                'trades': int(stats['# Trades']),
                'win_rate': float(stats['Win Rate [%]']),
                'profit_factor': float(stats.get('Profit Factor', 0)),
                'avg_trade': float(stats.get('Avg. Trade', 0)),
                'best_trade': float(stats.get('Best Trade', 0)),
                'worst_trade': float(stats.get('Worst Trade', 0))
            }
            
        except Exception as e:
            logger.error(f"Error running backtest for {self.symbol}: {str(e)}")
            return {
                'symbol': self.symbol,
                'error': str(e)
            }
