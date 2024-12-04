"""Main script to run the backtesting system."""

import os
from loguru import logger
import pandas as pd
from tqdm import tqdm
import json
from datetime import datetime
import sys
from config import STRATEGY_PARAMS, LOG_FILE, RESULTS_DIR, INITIAL_CASH, COMMISSION, SHUFFLE_STOCKS
from data_manager import setup_test_data
from utils.data_loader import DataLoader
from strategies.buy_hold_strategy import BuyAndHoldStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.price_action_strategy import PriceActionStrategy
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
    return results_log

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
        results_log = setup_logging()
        
        # Store configuration info
        config_info = {
            "strategy": "Buy and Hold Strategy",
            "strategy_params": STRATEGY_PARAMS,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "initial_cash": INITIAL_CASH,
            "commission": COMMISSION
        }
        
        # Setup test data
        if SHUFFLE_STOCKS:
            setup_test_data()
        
        # Print initial message to console
        print("\nStarting backtesting process...")
        print("Loading stock data...")
        
        # Load all stock data
        stock_data = DataLoader.load_all_stocks()
        
        if not stock_data:
            print("Error: No stock data found. Please ensure test data directory contains CSV files.")
            return
        
        print(f"Found {len(stock_data)} stocks to process")
        
        # Initialize strategy
        strategy = PriceActionStrategy(STRATEGY_PARAMS)
        
        # Run backtest for each stock
        results = []
        total_stocks = len(stock_data)
        
        print("\nStarting backtesting...")
        
        # Show progress bar in console
        progress_bar = tqdm(total=total_stocks, 
                          desc="Progress", 
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]")
        
        for i, (symbol, data) in enumerate(stock_data.items(), 1):
            # Update status message below progress bar
            progress_bar.set_description(f"Testing {symbol}")
            
            engine = BacktestEngine(data, strategy, symbol)
            result = engine.run()
            results.append(result)
            
            # Update progress
            progress_bar.update(1)
            
            # Update status message
            if 'error' in result:
                progress_bar.set_postfix_str(f"{symbol}: Failed")
            else:
                progress_bar.set_postfix_str(f"{symbol}: {result['return']:.2f}%")
        
        progress_bar.close()
        
        # Process summary statistics
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

        # Start with a clean log file
        with open(results_log, 'w') as f:
            # 1. Overall Summary
            f.write("\n" + "="*50 + "\n")
            f.write("OVERALL BACKTESTING SUMMARY\n")
            f.write("="*50 + "\n")
            f.write(json.dumps(summary_stats, indent=2) + "\n")
            
            # 2. Individual Stock Results
            f.write("\n" + "="*50 + "\n")
            f.write("INDIVIDUAL STOCK RESULTS\n")
            f.write("="*50 + "\n")
            for result in results:
                if 'error' in result:
                    f.write(f"\nStock: {result['symbol']}\n")
                    f.write(f"Status: Failed\n")
                    f.write(f"Error: {result['error']}\n")
                else:
                    f.write(f"\nStock: {result['symbol']}\n")
                    f.write(f"Status: Success\n")
                    f.write(f"Return: {result['return']:.2f}%\n")
                    f.write(f"Sharpe Ratio: {result['sharpe']:.2f}\n")
                    f.write(f"Max Drawdown: {result['max_drawdown']:.2f}%\n")
                    f.write(f"Win Rate: {result['win_rate']:.2f}%\n")
                    f.write(f"Number of Trades: {result['trades']}\n")
                    f.write(f"Profit Factor: {result['profit_factor']:.2f}\n")
                    f.write(f"Average Trade: ${result['avg_trade']:.2f}\n")
                    f.write(f"Best Trade: ${result['best_trade']:.2f}\n")
                    f.write(f"Worst Trade: ${result['worst_trade']:.2f}\n")
            
            # 3. Configuration Details
            f.write("\n" + "="*50 + "\n")
            f.write("CONFIGURATION DETAILS\n")
            f.write("="*50 + "\n")
            f.write(json.dumps(config_info, indent=2) + "\n")
        
        # Print final summary to console
        print("\n" + "="*50)
        print("Backtesting completed!")
        print(f"Total stocks processed: {len(results)}")
        print(f"Successful tests: {len(successful_results)}")
        print(f"Failed tests: {len(results) - len(successful_results)}")
        if successful_results:
            print(f"Average Return: {summary_stats['average_return']:.2f}%")
            best_stock = summary_stats['best_stock']
            print(f"Best Performer: {best_stock['symbol']} ({best_stock['return']:.2f}%)")
        print(f"\nDetailed results saved to: {results_log}")
        print("="*50)
        
    except Exception as e:
        print(f"\nError in main execution: {str(e)}")
        logger.exception("Error in main execution:")

if __name__ == "__main__":
    main()