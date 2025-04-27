#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import random
import logging
import json
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from .data_processor import DataProcessor

class RestaurantCrawler:
    def __init__(self):
        self.setup_logging()
        self.session_count = 0
        self.max_session_requests = random.randint(8, 15)
        self.data_processor = DataProcessor()
        
    def setup_logging(self):
        """設置日誌"""
        self.logger = logging.getLogger("RestaurantCrawler")
    
    def create_browser(self, headless=False):
        """創建並配置瀏覽器實例 - 強制英文設置"""
        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        # 模擬真實用戶
        user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        ]
        options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # 強制設置語言為英文
        options.add_argument("--lang=en-US")
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en',
            'profile.default_content_setting_values.geolocation': 1,
            'profile.default_content_setting_values.notifications': 2
        })
        
        # 禁用自動化檢測特性
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        # 添加隨機的視窗大小
        window_width = random.randint(1024, 1920)
        window_height = random.randint(768, 1080)
        options.add_argument(f"--window-size={window_width},{window_height}")
        
        # 其他設置
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 執行 JavaScript 來設置語言屬性
        driver.execute_script("""
            Object.defineProperty(navigator, 'language', {
                get: function() { return 'en-US'; }
            });
            Object.defineProperty(navigator, 'languages', {
                get: function() { return ['en-US', 'en']; }
            });
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.logger.info("Browser created with English language settings")
        
        return driver
    
    def human_like_delay(self, min_sec=3, max_sec=7):
        """模擬人類操作的延遲時間"""
        base_delay = random.uniform(min_sec, max_sec)
        extra_delay = random.expovariate(0.5)
        total_delay = base_delay + min(extra_delay, 5)
        
        self.logger.info(f"Waiting {total_delay:.2f} seconds")
        time.sleep(total_delay)
    
    def type_like_human(self, element, text):
        """模擬人類打字節奏"""
        for char in text:
            element.send_keys(char)
            # 打字間隔時間隨機化
            char_delay = random.uniform(0.05, 0.25)
            time.sleep(char_delay)
            
            # 偶爾添加較長的停頓
            if random.random() < 0.1:  # 10%機率
                time.sleep(random.uniform(0.3, 0.7))
    
    def slow_scroll(self, driver, max_scrolls=50):
        """緩慢滾動頁面以載入更多評論"""
        current_position = 0
        last_review_count = 0
        unchanged_count = 0
        
        try:
            review_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"))
            )
        except:
            self.logger.warning("找不到評論容器，無法滾動加載更多評論")
            return
        
        for scroll_attempt in range(max_scrolls):
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
            current_review_count = len(reviews)
            
            if current_review_count == last_review_count:
                unchanged_count += 1
                if unchanged_count >= 3:
                    self.logger.info(f"已載入所有評論: {current_review_count} 條 (連續 {unchanged_count} 次未變化)")
                    break
            else:
                unchanged_count = 0
                
            last_review_count = current_review_count
            self.logger.info(f"當前已加載 {current_review_count} 條評論 (滾動次數: {scroll_attempt + 1}/{max_scrolls})")
            
            scroll_distance = random.randint(300, 800)
            current_position += scroll_distance
            
            driver.execute_script(f"arguments[0].scrollTop = {current_position};", review_container)
            
            if random.random() < 0.2:  # 20%機率
                try:
                    driver.execute_script("arguments[0].click();", review_container)
                except:
                    pass
            
            pause_time = random.uniform(1.5, 4.5)
            time.sleep(pause_time)
    
    def expand_all_reviews(self, driver):
        """展開所有評論的完整內容"""
        try:
            more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
            expanded_count = 0
            
            for button in more_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(random.uniform(0.3, 0.7))
                    button.click()
                    expanded_count += 1
                    time.sleep(random.uniform(0.5, 1.0))
                except:
                    continue
            
            self.logger.info(f"已展開 {expanded_count} 條評論的完整內容")
        except Exception as e:
            self.logger.error(f"展開評論時出錯: {str(e)}")
    
    def extract_review_text(self, review_element):
        """提取評論文本，嘗試多種選擇器以獲取完整內容"""
        try:
            try:
                review_text = review_element.find_element(By.CSS_SELECTOR, "span.wiI7pd").text
            except:
                try:
                    review_text = review_element.find_element(By.CSS_SELECTOR, "div.MyEned").text
                except:
                    try:
                        review_text = review_element.find_element(By.CSS_SELECTOR, "div[jsinstance]").text
                    except:
                        review_text = ""
            
            return review_text
        except:
            return ""
    
    def save_progress(self, processed_urls):
        """保存當前進度"""
        with open("data/raw/progress.json", "w", encoding='utf-8') as f:
            json.dump({
                "processed_urls": processed_urls,
                "timestamp": time.time()
            }, f, ensure_ascii=False)
        self.logger.info("進度已保存")

    def load_progress(self):
        """載入上一次的進度"""
        try:
            with open("data/raw/progress.json", "r", encoding='utf-8') as f:
                progress = json.load(f)
            self.logger.info(f"已載入進度，上次運行時間: {datetime.fromtimestamp(progress['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
            return progress["processed_urls"]
        except:
            self.logger.info("沒有找到進度文件，將從頭開始")
            return []
    
    def crawl_restaurants(self, restaurant_urls):
        """爬取多個餐廳的評論"""
        total_reviews = 0
        processed_count = 0
        
        processed_urls = self.load_progress()
        
        urls_to_process = [url for url in restaurant_urls if url not in processed_urls]
        
        self.logger.info(f"共有 {len(urls_to_process)} 家餐廳待處理")
        
        for url in urls_to_process:
            if self.session_count >= self.max_session_requests:
                self.logger.info(f"已處理 {self.session_count} 個請求，休息一段時間...")
                sleep_time = random.uniform(10*60, 13*60)
                self.logger.info(f"休息 {sleep_time/60:.1f} 分鐘")
                time.sleep(sleep_time)
                
                self.session_count = 0
                self.max_session_requests = random.randint(8, 15)
            
            driver = self.create_browser()
            
            try:
                reviews_count = self.extract_restaurant_data(driver, url)
                total_reviews += reviews_count
                processed_count += 1
                
                processed_urls.append(url)
                
                if processed_count % 3 == 0:  # 每處理3家餐廳保存一次進度
                    self.save_progress(processed_urls)
                
                self.logger.info(f"已處理 {processed_count}/{len(urls_to_process)} 家餐廳，總計 {total_reviews} 條評論")
                
                rest_time = random.uniform(1*60, 4*60) 
                self.logger.info(f"休息 {rest_time/60:.1f} 分鐘後繼續")
                time.sleep(rest_time)
                
            except Exception as e:
                self.logger.error(f"處理餐廳時發生錯誤: {str(e)}")
            
            finally:
                driver.quit()
                self.session_count += 1
        
        self.save_progress(processed_urls)
        
        self.logger.info(f"爬取完成! 共處理 {processed_count} 家餐廳, {total_reviews} 條評論")
    
    def collect_restaurant_urls(self, search_terms, locations):
        """收集餐廳URL清單"""
        restaurant_urls = []
        
        driver = self.create_browser()
        
        try:
            for location in locations:
                for term in search_terms:
                    search_query = f"{term} in {location}, USA"
                    self.logger.info(f"Searching: {search_query}")
                    
                    driver.get("https://www.google.com/maps?hl=en")
                    self.human_like_delay()
                    
                    search_box = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "searchboxinput"))
                    )
                    search_box.clear()
                    self.type_like_human(search_box, search_query)
                    
                    search_button = driver.find_element(By.ID, "searchbox-searchbutton")
                    search_button.click()
                    self.human_like_delay()
                    
                    items = WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.Nv2PK"))
                    )
                    
                    for i, item in enumerate(items[:10]):
                        try:
                            item.click()
                            self.human_like_delay()
                            
                            current_url = driver.current_url
                            restaurant_urls.append(current_url)
                            
                            self.logger.info(f"Collected restaurant URL: {current_url}")
                        except Exception as e:
                            self.logger.error(f"Error collecting restaurant URL: {str(e)}")
                    
                    rest_time = random.uniform(1*60, 2*60)  
                    self.logger.info(f"Resting for {rest_time/60:.1f} minutes")
                    time.sleep(rest_time)
        
        except Exception as e:
            self.logger.error(f"Error collecting restaurant URLs: {str(e)}")
        
        finally:
            driver.quit()
        
        unique_urls = list(set(restaurant_urls))
        self.logger.info(f"Collected {len(unique_urls)} restaurant URLs")
        
        with open("data/raw/restaurant_urls.json", "w", encoding='utf-8') as f:
            json.dump(unique_urls, f, ensure_ascii=False)
        
        return unique_urls
    
    def extract_restaurant_data(self, driver, url):
        """提取餐廳基本信息和評論"""
        try:
            english_url = url
            if "?hl=" not in url:
                english_url = url + "&hl=en"
            driver.get(english_url)
            self.human_like_delay(5, 8)
            
            try:
                restaurant_name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
            except:
                restaurant_name = "Unknown restaurant"
                self.logger.warning("Could not get restaurant name")
            
            try:
                address = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']").text
            except:
                address = "Unknown address"
                
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "div.F7nice")
                rating = rating_element.find_element(By.CSS_SELECTOR, "span.ceNzKf").text
                reviews_count = rating_element.find_element(By.CSS_SELECTOR, "span.HHrUdb").text
            except:
                rating = "No rating"
                reviews_count = "0"
            
            try:
                review_selectors = [
                    "//button[contains(@aria-label, 'Reviews')]", 
                    "//div[contains(text(), 'Reviews')]",
                    "//button[contains(., 'Reviews')]",
                    "//button[contains(@aria-label, 'review')]",
                    "//div[contains(text(), 'review')]"
                ]
                
                for selector in review_selectors:
                    try:
                        reviews_tab = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        reviews_tab.click()
                        self.logger.info("Successfully clicked reviews tab")
                        self.human_like_delay(3, 5)
                        break
                    except:
                        continue
            except Exception as e:
                self.logger.warning(f"Could not click reviews tab: {str(e)}")
            
            self.slow_scroll(driver, max_scrolls=50)
            
            self.expand_all_reviews(driver)
            
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
            self.logger.info(f"Found {len(review_elements)} reviews")
            
            reviews_data = []
            
            for review in review_elements:
                try:
                    try:
                        reviewer_name = review.find_element(By.CSS_SELECTOR, "div.d4r55").text
                    except:
                        reviewer_name = "Anonymous"
                    
                    try:
                        rating_element = review.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                        rating = rating_element.get_attribute("aria-label")
                    except:
                        rating = "No rating"
                    
                    try:
                        review_date = review.find_element(By.CSS_SELECTOR, "span.rsqaWe").text
                    except:
                        review_date = "Unknown date"
                    
                    review_text = self.extract_review_text(review)
                    
                    photos = []
                    try:
                        photo_elements = review.find_elements(By.CSS_SELECTOR, "div.KtCyie img.STQFb")
                        for photo in photo_elements:
                            try:
                                photo_url = photo.get_attribute("src")
                                if photo_url:
                                    photos.append(photo_url)
                            except:
                                pass
                    except:
                        pass
                    
                    tags = []
                    try:
                        tag_elements = review.find_elements(By.CSS_SELECTOR, "div.m6QErb div.NGLBjb")
                        for tag in tag_elements:
                            try:
                                tag_text = tag.text
                                if tag_text:
                                    tags.append(tag_text)
                            except:
                                pass
                    except:
                        pass
                    
                    review_data = {
                        "reviewer_name": reviewer_name,
                        "rating": rating,
                        "date": review_date,
                        "text": review_text,
                        "photos": photos,
                        "tags": tags
                    }
                    
                    reviews_data.append(review_data)
                    
                except Exception as e:
                    self.logger.error(f"Error extracting single review: {str(e)}")
            
            restaurant_data = {
                "name": restaurant_name,
                "address": address,
                "overall_rating": rating,
                "reviews_count": reviews_count,
                "url": url,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "reviews": reviews_data
            }
            
            self.data_processor.append_to_master_file(restaurant_data)
            
            return len(reviews_data)
        
        except Exception as e:
            self.logger.error(f"Error processing restaurant: {str(e)}")
            return 0