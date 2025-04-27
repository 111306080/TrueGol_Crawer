#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import json
import glob
import os
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger("DataProcessor")
        self.master_file = "data/processed/all_restaurants.json"
    
    def append_to_master_file(self, restaurant_data):
        """Append restaurant data to single master file instead of creating separate files"""
        try:
            # Load existing data
            if os.path.exists(self.master_file):
                with open(self.master_file, 'r', encoding='utf-8') as f:
                    master_data = json.load(f)
            else:
                master_data = {
                    "restaurants": [],
                    "total_restaurants": 0,
                    "total_reviews": 0,
                    "last_updated": ""
                }
            
            # Append new restaurant data
            master_data["restaurants"].append(restaurant_data)
            master_data["total_restaurants"] = len(master_data["restaurants"])
            master_data["total_reviews"] = sum(len(r.get("reviews", [])) for r in master_data["restaurants"])
            master_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save back to master file
            os.makedirs(os.path.dirname(self.master_file), exist_ok=True)
            with open(self.master_file, 'w', encoding='utf-8') as f:
                json.dump(master_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Restaurant data appended to master file: {self.master_file}")
            
        except Exception as e:
            self.logger.error(f"Error appending to master file: {str(e)}")
    
    def merge_existing_files(self, raw_data_dir="data/raw"):
        """Merge existing separate JSON files into one master file"""
        # Get all restaurant JSON files (excluding URL list)
        json_files = glob.glob(os.path.join(raw_data_dir, "restaurant_*.json"))
        json_files = [f for f in json_files if not f.endswith("restaurant_urls.json")]
        
        all_data = []
        
        for file in json_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.append(data)
            except Exception as e:
                self.logger.error(f"Error reading {file}: {str(e)}")
        
        # Create merged data structure
        merged_data = {
            "restaurants": all_data,
            "total_restaurants": len(all_data),
            "total_reviews": sum(len(r.get("reviews", [])) for r in all_data),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save merged data
        os.makedirs(os.path.dirname(self.master_file), exist_ok=True)
        with open(self.master_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Successfully merged {len(all_data)} restaurant files into {self.master_file}")
        
        # Optionally, delete individual files after merging
        # for file in json_files:
        #     os.remove(file)
        
        return merged_data