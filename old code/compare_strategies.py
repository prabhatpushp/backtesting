"""Script to compare different trading strategies."""

import os
from loguru import logger
import pandas as pd
from tqdm import tqdm
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

from config import (
    STRATEGY_PARAMS, RESULTS_DIR, INITIAL_CASH, 
    COMMISSION, SHUFFLE_STOCKS
)
from data_manager import setup_test_data
from utils.data_loader import DataLoader
from strategies.buy_hold_strategy import BuyAndHoldStrategy
from strategies.moving_average_strategy import MovingAverageStrategy
from strategies.price_action_strategy import PriceActionStrategy
from strategies.percentage_change_strategy import PercentageChangeStrategy
from backtester import BacktestEngine

def setup_strategies():
    """Initialize all strategies to be compared."""
    strategies = {
        "Buy and Hold": BuyAndHoldStrategy(STRATEGY_PARAMS),
        "Moving Average": MovingAverageStrategy(STRATEGY_PARAMS),
        "Price Action": PriceActionStrategy(STRATEGY_PARAMS),
        "Percentage Change": PercentageChangeStrategy(STRATEGY_PARAMS)
    }
    return strategies

def run_comparison(stock_data, strategies):
    """Run backtests for all strategies on all stocks."""
    comparison_results = {}
    
    for strategy_name, strategy in strategies.items():
        print(f"\nTesting {strategy_name} Strategy...")
        strategy_results = []
        
        progress_bar = tqdm(total=len(stock_data), 
                          desc=f"{strategy_name}", 
                          bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}")
        
        for symbol, data in stock_data.items():
            engine = BacktestEngine(data, strategy, symbol)
            result = engine.run()
            strategy_results.append(result)
            progress_bar.update(1)
        
        progress_bar.close()
        comparison_results[strategy_name] = strategy_results
    
    return comparison_results

def calculate_strategy_metrics(results):
    """Calculate key metrics for each strategy."""
    metrics = {}
    
    for strategy_name, strategy_results in results.items():
        # Filter out failed results
        successful_results = [r for r in strategy_results if 'error' not in r]
        
        if not successful_results:
            metrics[strategy_name] = {
                'average_return': 0,
                'win_rate': 0,
                'total_trades': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
            continue
        
        metrics[strategy_name] = {
            'average_return': sum(r['return'] for r in successful_results) / len(successful_results),
            'win_rate': len([r for r in successful_results if r['return'] > 0]) / len(successful_results),
            'total_trades': sum(r.get('total_trades', 0) for r in successful_results),
            'max_drawdown': sum(r['max_drawdown'] for r in successful_results) / len(successful_results),
            'sharpe_ratio': sum(r['sharpe'] for r in successful_results) / len(successful_results)
        }
    
    return metrics

def plot_comparison(metrics):
    """Create visualization comparing strategy performances."""
    # Set up the plot style
    plt.style.use('seaborn')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Prepare data
    strategies = list(metrics.keys())
    returns = [m['average_return'] * 100 for m in metrics.values()]
    win_rates = [m['win_rate'] * 100 for m in metrics.values()]
    trades = [m['total_trades'] for m in metrics.values()]
    drawdowns = [abs(m['max_drawdown']) * 100 for m in metrics.values()]
    
    # Plot average returns
    ax1.bar(strategies, returns)
    ax1.set_title('Average Return (%)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Plot win rates
    ax2.bar(strategies, win_rates)
    ax2.set_title('Win Rate (%)')
    ax2.tick_params(axis='x', rotation=45)
    
    # Plot total trades
    ax3.bar(strategies, trades)
    ax3.set_title('Total Number of Trades')
    ax3.tick_params(axis='x', rotation=45)
    
    # Plot max drawdowns
    ax4.bar(strategies, drawdowns)
    ax4.set_title('Maximum Drawdown (%)')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # Save the plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(os.path.join(RESULTS_DIR, f'strategy_comparison_{timestamp}.png'))
    plt.close()

def save_comparison_results(metrics):
    """Save comparison results to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_DIR, f'strategy_comparison_{timestamp}.json')
    
    with open(results_file, 'w') as f:
        json.dump(metrics, f, indent=4)
    
    return results_file

def main():
    """Main function to execute the strategy comparison."""
    try:
        # Create results directory if it doesn't exist
        os.makedirs(RESULTS_DIR, exist_ok=True)
        
        # Setup test data if needed
        if SHUFFLE_STOCKS:
            setup_test_data()
        
        print("\nStarting strategy comparison...")
        print("Loading stock data...")
        
        # Load stock data
        stock_data = DataLoader.load_all_stocks()
        
        if not stock_data:
            print("Error: No stock data found. Please ensure test data directory contains CSV files.")
            return
        
        print(f"Found {len(stock_data)} stocks to process")
        
        # Initialize strategies
        strategies = setup_strategies()
        
        # Run comparison
        results = run_comparison(stock_data, strategies)
        
        # Calculate metrics
        metrics = calculate_strategy_metrics(results)
        
        # Plot results
        print("\nGenerating comparison plots...")
        plot_comparison(metrics)
        
        # Save results
        results_file = save_comparison_results(metrics)
        
        print("\nComparison completed successfully!")
        print(f"Results saved to: {results_file}")
        
        # Print summary
        print("\nStrategy Performance Summary:")
        print("-" * 50)
        for strategy, metric in metrics.items():
            print(f"\n{strategy}:")
            print(f"Average Return: {metric['average_return']*100:.2f}%")
            print(f"Win Rate: {metric['win_rate']*100:.2f}%")
            print(f"Total Trades: {metric['total_trades']}")
            print(f"Max Drawdown: {metric['max_drawdown']*100:.2f}%")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
