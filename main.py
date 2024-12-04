"""Main script to run the backtesting system."""

import os
from loguru import logger
import pandas as pd
from tqdm import tqdm
import json
from datetime import datetime
from config import STRATEGY_PARAMS, LOG_FILE, RESULTS_DIR, INITIAL_CASH, COMMISSION
from utils.data_loader import DataLoader
from strategies.buy_hold_strategy import BuyAndHoldStrategy
from backtester import BacktestEngine

def setup_logging():
    """Configure logging settings."""
    # Create results directory if it doesn't exist
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Create a timestamped results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_log = os.path.join(RESULTS_DIR, f"backtest_results_{timestamp}.log")
    
    # Remove any existing handlers
    logger.remove()
    
    # Add file handler for the results log
    logger.add(results_log, format="{message}", level="INFO")

def save_final_results(results, config_info):
    """Save final results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_DIR, f"backtest_summary_{timestamp}.json")
    
    final_results = {
        "configuration": config_info,
        "results": results
    }
    
    return results_file

def main():
    """Main function to execute the backtesting process."""
    try:
        # Setup logging
        setup_logging()
        
        # Store configuration info
        config_info = {
            "strategy": "Buy and Hold Strategy",
            "strategy_params": STRATEGY_PARAMS,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "initial_cash": INITIAL_CASH,
            "commission": COMMISSION
        }
        
        # Log configuration
        logger.info("\n=== Backtesting Configuration ===")
        logger.info(json.dumps(config_info, indent=2))
        logger.info("\n=== Starting Backtesting Process ===")
        
        # Load all stock data
        logger.info("Loading stock data...")
        stock_data = DataLoader.load_all_stocks()
        
        if not stock_data:
            logger.error("No stock data found. Please ensure test data directory contains CSV files.")
            return
        
        # Initialize strategy
        strategy = BuyAndHoldStrategy(STRATEGY_PARAMS)
        
        # Run backtest for each stock
        results = []
        for symbol, data in tqdm(stock_data.items(), desc="Running backtests"):
            engine = BacktestEngine(data, strategy, symbol)
            result = engine.run()
            results.append(result)
        
        # Process and log summary statistics
        successful_results = [r for r in results if 'error' not in r]
        
        summary_stats = {
            "total_stocks": len(results),
            "successful_tests": len(successful_results),
            "failed_tests": len(results) - len(successful_results)
        }
        
        if successful_results:
            summary_stats.update({
                "average_return": sum(r['return'] for r in successful_results) / len(successful_results),
                "average_sharpe": sum(r['sharpe'] for r in successful_results) / len(successful_results),
                "average_drawdown": sum(r['max_drawdown'] for r in successful_results) / len(successful_results),
                "best_stock": max(successful_results, key=lambda x: x['return']),
                "worst_stock": min(successful_results, key=lambda x: x['return'])
            })
        
        # Log summary statistics
        logger.info("\n=== Overall Backtesting Summary ===")
        logger.info(json.dumps(summary_stats, indent=2))
        
        # Save final results
        final_results = {
            "summary_stats": summary_stats,
            "individual_results": results
        }
        
        results_file = save_final_results(final_results, config_info)
        logger.info(f"\nComplete results saved to: {results_file}")
        
    except Exception as e:
        logger.exception("Error in main execution:")

if __name__ == "__main__":
    main()