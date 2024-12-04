"""Module for managing data operations between stocks and test data directories."""

import os
import shutil
import random
from typing import List
import logging

from config import STOCKS_DIR, TEST_DATA_DIR, NUM_FILES_TO_COPY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def clean_test_directory() -> None:
    """Remove all files from the test data directory if they exist."""
    if os.path.exists(TEST_DATA_DIR):
        logging.info("Cleaning test data directory...")
        for file_name in os.listdir(TEST_DATA_DIR):
            file_path = os.path.join(TEST_DATA_DIR, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                    logging.debug(f"Deleted: {file_name}")
            except Exception as e:
                logging.error(f"Error deleting {file_name}: {str(e)}")
    else:
        os.makedirs(TEST_DATA_DIR)
        logging.info("Created test data directory")

def get_stock_files() -> List[str]:
    """Get list of all stock files from the stocks directory."""
    if not os.path.exists(STOCKS_DIR):
        raise FileNotFoundError(f"Stocks directory not found at: {STOCKS_DIR}")
    
    return [f for f in os.listdir(STOCKS_DIR) if os.path.isfile(os.path.join(STOCKS_DIR, f))]

def copy_random_files() -> None:
    """Copy random files from stocks to test data directory."""
    stock_files = get_stock_files()
    
    if not stock_files:
        raise FileNotFoundError("No stock files found in the stocks directory")
    
    # Determine number of files to copy (minimum of available files and desired number)
    num_files = min(len(stock_files), NUM_FILES_TO_COPY)
    selected_files = random.sample(stock_files, num_files)
    
    logging.info(f"Copying {num_files} random files to test data...")
    
    for file_name in selected_files:
        source = os.path.join(STOCKS_DIR, file_name)
        destination = os.path.join(TEST_DATA_DIR, file_name)
        try:
            shutil.copy2(source, destination)
            logging.info(f"Copied: {file_name}")
        except Exception as e:
            logging.error(f"Error copying {file_name}: {str(e)}")

def setup_test_data() -> None:
    """Main function to set up test data."""
    try:
        clean_test_directory()
        copy_random_files()
        logging.info("Test data setup completed successfully")
    except Exception as e:
        logging.error(f"Error setting up test data: {str(e)}")
        raise
