"""Configuration settings for the backtesting system."""

import os
from datetime import datetime

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCKS_DIR = os.path.join(BASE_DIR, "stocks")
TEST_DATA_DIR = os.path.join(BASE_DIR, "test data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Number of files to copy
NUM_FILES_TO_COPY = 10
SHUFFLE_STOCKS = True

# Create necessary directories
for directory in [RESULTS_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Backtesting settings
INITIAL_CASH = 100000  # Starting capital
MAX_POSITIONS = 5      # Maximum number of simultaneous positions
POSITION_SIZE = 0.2    # Size of each position (20% of portfolio)
COMMISSION = 0.001     # 0.1% commission per trade

# Strategy Parameters (example for Moving Average Crossover)
STRATEGY_PARAMS = {
    'MA_FAST': 20,
    'MA_SLOW': 50,
    'RSI_PERIOD': 14,
    'RSI_OVERBOUGHT': 70,
    'RSI_OVERSOLD': 30,
    'STOP_LOSS': 0.05,  # 5% stop loss
    'TAKE_PROFIT': 0.15  # 15% take profit
}

# Logging settings
LOG_FILE = os.path.join(LOG_DIR, f'backtest_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
LOG_LEVEL = 'INFO'

# Results settings
PLOT_RESULTS = True
SAVE_TRADES = True
RESULTS_FILE = os.path.join(RESULTS_DIR, f'results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
