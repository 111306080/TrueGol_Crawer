#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import logging
from src.crawler import RestaurantCrawler
from src.data_processor import DataProcessor

def setup_directories():
    """設置必要的目錄結構"""
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

def main():
    # Setup directories
    setup_directories()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/crawler.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("MainApp")
    
    # Initialize crawler
    crawler = RestaurantCrawler()
    data_processor = DataProcessor()
    
    # City list
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
              "San Antonio", "San Diego", "Dallas", "San Francisco"]
    
    # Restaurant types in English
    restaurant_types = ["Japanese Restaurant", "Chinese Restaurant", "Italian Restaurant", 
                      "Vegetarian Restaurant", "Korean Restaurant", "Cafe"]
    
    # Phase 1: Collect restaurant URLs
    try:
        # Try to load saved URL list
        with open("data/raw/restaurant_urls.json", "r", encoding='utf-8') as f:
            restaurant_urls = json.load(f)
        logger.info(f"Loaded {len(restaurant_urls)} restaurant URLs from file")
    except:
        # If no saved URLs, collect new ones
        restaurant_urls = crawler.collect_restaurant_urls(restaurant_types, cities)
    
    # Phase 2: Crawl restaurant reviews
    crawler.crawl_restaurants(restaurant_urls)
    
    # Phase 3: Merge any existing individual files (if needed)
    if os.path.exists("data/raw/restaurant_*.json"):
        data_processor.merge_existing_files()
    
    logger.info("Crawling completed successfully!")

if __name__ == "__main__":
    main()