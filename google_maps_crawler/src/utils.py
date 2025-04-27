#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import json
from datetime import datetime
import os

def ensure_directory_exists(directory):
    """確保目錄存在，如不存在則創建"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def random_delay(min_seconds=1, max_seconds=5):
    """生成隨機延遲時間"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def save_json(data, filename):
    """保存數據為JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json(filename):
    """載入JSON文件"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def get_timestamp():
    """獲取當前時間戳"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def extract_rating_value(rating_text):
    """從評分文本中提取數值"""
    try:
        if not rating_text or rating_text == "無評分":
            return None
        # 處理形如 "5 顆星" 或 "5 stars out of 5" 的文本
        parts = rating_text.split()
        return float(parts[0])
    except (ValueError, IndexError):
        return None