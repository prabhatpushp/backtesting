import os
import json
import logging
import datetime
from typing import Dict
import pandas as pd
from backtesting import Backtest
from data_loader import DataLoader
from data_randomiser import DataRandomizer
from strategies.sma_cross import SMACross
from tqdm import tqdm

class BacktestRunner:
    """
    Main class to orchestrate the backtesting process
    """
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the backtest runner
        
        Args:
            config_path (str): Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Create results directory first
        self.results_dir = self._create_results_directory()
        
        # Setup logging to both file and console
        log_file = os.path.join(self.results_dir, "backtest.log")
        logging.basicConfig(
            level=self.config['logging']['level'],
            format=self.config['logging']['format'],
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.data_loader = DataLoader(config_path)
        self.data_randomizer = DataRandomizer(config_path)
    
    def _create_results_directory(self) -> str:
        """
        Create a timestamped results directory
        
        Returns:
            str: Path to results directory
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = os.path.join(
            self.config['results']['output_dir'],
            f"backtest_results_{timestamp}"
        )
        os.makedirs(results_dir, exist_ok=True)
        
        # Save configuration
        config_file = os.path.join(results_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        
        return results_dir
    
    def _save_results(self, symbol: str, results: Dict) -> None:
        """
        Save backtest results for a stock
        
        Args:
            symbol (str): Stock symbol
            results (Dict): Backtest results
        """
        if self.config['results']['save_metrics']:
            # Save trade details
            metrics_file = os.path.join(self.results_dir, f"{symbol}_metrics.json")
            trades_dict = {}
            for idx, trade in results._trades.iterrows():
                trade_dict = {}
                for col in trade.index:
                    if isinstance(trade[col], pd.Timestamp):
                        trade_dict[col] = trade[col].isoformat()
                    else:
                        trade_dict[col] = trade[col]
                trades_dict[str(idx)] = trade_dict
            
            with open(metrics_file, 'w') as f:
                json.dump(trades_dict, f, indent=4)
            
            # Save performance metrics
            stats_file = os.path.join(self.results_dir, f"{symbol}_stats.json")
            stats_dict = {}
            for key, value in results.stats.items():
                if isinstance(value, pd.Timestamp):
                    stats_dict[key] = value.isoformat()
                else:
                    stats_dict[key] = value
            
            with open(stats_file, 'w') as f:
                json.dump(stats_dict, f, indent=4)
    
    def run(self) -> None:
        """
        Run the backtesting process
        """
        self.logger.info("Starting backtesting process")
        
        # Randomize test data if enabled
        if self.config['randomizer']['enabled']:
            self.logger.info("Randomizing test stocks")
            self.data_randomizer.randomize_stocks()
        
        # Load test data
        self.logger.info("Loading test data")
        test_stocks = self.data_loader.load_all_stocks(
            self.config['data']['test_data_dir']
        )
        
        if not test_stocks:
            self.logger.error("No test stocks found")
            return
        
        self.logger.info(f"Running backtests on {len(test_stocks)} stocks")
        
        # Run backtest for each stock with progress bar
        for symbol in tqdm(test_stocks.keys(), desc="Running backtests"):
            data = test_stocks[symbol]
            self.logger.info(f"Running backtest for {symbol}")
            
            try:
                # Initialize backtest
                bt = Backtest(
                    data,
                    SMACross,
                    cash=self.config['initial_cash'],
                    commission=self.config['commission']                    
                )
                
                # Run backtest
                results = bt.run()
                self.logger.info(f"Backtest completed for {symbol}")
                
                # Save results
                self._save_results(symbol, results)
                
                # Generate and save plot if enabled
                if self.config['results']['save_plots']:
                    plot_file = os.path.join(self.results_dir, f"{symbol}_plot.html")
                    bt.plot(filename=plot_file, open_browser=False)
                    self.logger.info(f"Plot saved for {symbol}")
            
            except Exception as e:
                self.logger.error(f"Error running backtest for {symbol}: {str(e)}")
        
        self.logger.info("Backtesting process completed")

if __name__ == "__main__":
    runner = BacktestRunner()
    runner.run()