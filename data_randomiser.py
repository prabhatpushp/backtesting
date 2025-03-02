import os
import json
import random
import shutil
import logging
from typing import List

class DataRandomizer:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.logger = logging.getLogger(__name__)
        self.stocks_dir = self.config['data']['stocks_dir']
        self.test_data_dir = self.config['data']['test_data_dir']
        self.randomizer_config = self.config['randomizer']
        
        if self.randomizer_config['random_seed']:
            random.seed(self.randomizer_config['random_seed'])
    
    def clean_test_directory(self) -> None:
        if os.path.exists(self.test_data_dir):
            for filename in os.listdir(self.test_data_dir):
                file_path = os.path.join(self.test_data_dir, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception:
                    pass
        else:
            os.makedirs(self.test_data_dir)
    
    def get_available_stocks(self) -> List[str]:
        if not os.path.exists(self.stocks_dir):
            return []
        
        return [f for f in os.listdir(self.stocks_dir) 
                if f.endswith(self.config['data']['file_format'])]
    
    def randomize_stocks(self) -> None:
        if not self.randomizer_config['enabled']:
            return
        
        self.logger.info("Starting data randomization process")
        
        self.clean_test_directory()
        available_stocks = self.get_available_stocks()
        
        if not available_stocks:
            return
        
        num_stocks = min(
            self.randomizer_config['test_stocks_count'],
            len(available_stocks)
        )
        
        selected_stocks = random.sample(available_stocks, num_stocks)
        
        for stock_file in selected_stocks:
            source = os.path.join(self.stocks_dir, stock_file)
            destination = os.path.join(self.test_data_dir, stock_file)
            try:
                shutil.copy2(source, destination)
            except Exception:
                pass
        
        self.logger.info("Data randomization process completed")