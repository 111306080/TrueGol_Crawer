#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from datetime import datetime

class DataExtractor:
    def __init__(self):
        self.logger = logging.getLogger("DataExtractor")
    
    def extract_restaurant_info(self, driver):
        """提取餐廳基本信息"""
        restaurant_info = {}
        
        try:
            # 餐廳名稱
            try:
                restaurant_info["name"] = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
            except Exception as e:
                self.logger.error(f"獲取餐廳名稱時出錯: {str(e)}")
                restaurant_info["name"] = "未知餐廳"
        
            # 嘗試獲取地址
            try:
                address = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='address']").text
                restaurant_info["address"] = address
            except:
                restaurant_info["address"] = "未知地址"
                
            # 嘗試獲取評分
            try:
                rating_element = driver.find_element(By.CSS_SELECTOR, "div.F7nice")
                rating = rating_element.find_element(By.CSS_SELECTOR, "span.ceNzKf").text
                reviews_count = rating_element.find_element(By.CSS_SELECTOR, "span.HHrUdb").text
                restaurant_info["overall_rating"] = rating
                restaurant_info["reviews_count"] = reviews_count
            except:
                restaurant_info["overall_rating"] = "無評分"
                restaurant_info["reviews_count"] = "0"
            
            # 嘗試獲取餐廳類型
            try:
                categories = driver.find_elements(By.CSS_SELECTOR, "button[jsaction='pane.rating.category']")
                restaurant_info["categories"] = [cat.text for cat in categories]
            except:
                restaurant_info["categories"] = []
                
            # 嘗試獲取價格水平
            try:
                price_level = driver.find_element(By.CSS_SELECTOR, "span[aria-label*='Price:']").get_attribute("aria-label")
                restaurant_info["price_level"] = price_level
            except:
                restaurant_info["price_level"] = "未知價格水平"
                
            # 嘗試獲取營業時間
            try:
                hours_button = driver.find_element(By.CSS_SELECTOR, "div[data-item-id='oh']")
                hours_button.click()
                time.sleep(1)  # 等待營業時間面板展開
                
                hours_elements = driver.find_elements(By.CSS_SELECTOR, "tr.y0skZc")
                hours = []
                
                for element in hours_elements:
                    try:
                        day = element.find_element(By.CSS_SELECTOR, "td.T4OwTb").text
                        time_range = element.find_element(By.CSS_SELECTOR, "td.mxowUb").text
                        hours.append(f"{day}: {time_range}")
                    except:
                        pass
                
                restaurant_info["opening_hours"] = hours
            except:
                restaurant_info["opening_hours"] = []
            
            # 嘗試獲取電話號碼
            try:
                phone_button = driver.find_element(By.CSS_SELECTOR, "button[data-item-id='phone:tel']")
                phone = phone_button.text
                restaurant_info["phone"] = phone
            except:
                restaurant_info["phone"] = "未知電話"
            
            # 添加URL和抓取時間
            restaurant_info["url"] = driver.current_url
            restaurant_info["crawl_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            self.logger.error(f"提取餐廳基本信息時出錯: {str(e)}")
        
        return restaurant_info
    
    def extract_reviews(self, driver, max_scrolls=50):
        """提取餐廳評論"""
        reviews_data = []
        
        try:
            # 點擊"評論"標籤
            try:
                # 嘗試多種可能的選擇器找到評論標籤
                review_selectors = [
                    "//button[contains(@aria-label, '評論')]", 
                    "//button[contains(@aria-label, 'reviews')]",
                    "//div[contains(text(), '評論')]",
                    "//div[contains(text(), 'Reviews')]"
                ]
                
                for selector in review_selectors:
                    try:
                        reviews_tab = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        reviews_tab.click()
                        self.logger.info("成功點擊評論標籤")
                        time.sleep(random.uniform(2, 4))
                        break
                    except:
                        continue
            except Exception as e:
                self.logger.warning(f"點擊評論標籤時出錯: {str(e)}")
            
            # 滾動加載更多評論
            self._scroll_for_reviews(driver, max_scrolls)
            
            # 展開所有評論的完整內容
            self._expand_all_reviews(driver)
            
            # 提取評論
            review_elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
            
            for review in review_elements:
                review_data = {}
                
                # 提取評論者名稱
                try:
                    review_data["reviewer_name"] = review.find_element(By.CSS_SELECTOR, "div.d4r55").text
                except:
                    review_data["reviewer_name"] = "匿名用戶"
                
                # 提取評分
                try:
                    rating_element = review.find_element(By.CSS_SELECTOR, "span.kvMYJc")
                    review_data["rating"] = rating_element.get_attribute("aria-label")
                except:
                    review_data["rating"] = "無評分"
                
                # 提取日期
                try:
                    review_data["date"] = review.find_element(By.CSS_SELECTOR, "span.rsqaWe").text
                except:
                    review_data["date"] = "未知日期"
                
                # 提取評論文本
                review_data["text"] = self._extract_review_text(review)
                
                # 提取評論照片(如果有)
                try:
                    photo_elements = review.find_elements(By.CSS_SELECTOR, "div.KtCyie img.STQFb")
                    review_data["photos"] = [photo.get_attribute("src") for photo in photo_elements if photo.get_attribute("src")]
                except:
                    review_data["photos"] = []
                
                # 提取評論中的標籤
                try:
                    tags = review.find_elements(By.CSS_SELECTOR, "div.m6QErb div.NGLBjb")
                    review_data["tags"] = [tag.text for tag in tags if tag.text]
                except:
                    review_data["tags"] = []
                
                reviews_data.append(review_data)
            
            self.logger.info(f"成功提取 {len(reviews_data)} 條評論")
            
        except Exception as e:
            self.logger.error(f"提取評論時發生錯誤: {str(e)}")
        
        return reviews_data
    
    def _extract_review_text(self, review_element):
        """提取評論文本，嘗試多種選擇器以獲取完整內容"""
        try:
            # 先嘗試獲取展開後的完整評論文本
            try:
                review_text = review_element.find_element(By.CSS_SELECTOR, "span.wiI7pd").text
            except:
                # 嘗試其他可能的選擇器
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
    
    def _expand_all_reviews(self, driver):
        """展開所有評論的完整內容"""
        # 找到所有"更多"按鈕並點擊
        try:
            more_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
            expanded_count = 0
            
            for button in more_buttons:
                try:
                    # 確保按鈕在視野內
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
    
    def _scroll_for_reviews(self, driver, max_scrolls=50):
        """滾動頁面以載入更多評論"""
        current_position = 0
        last_review_count = 0
        unchanged_count = 0
        
        # 尋找評論容器
        try:
            review_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"))
            )
        except:
            self.logger.warning("找不到評論容器，無法滾動加載更多評論")
            return
        
        # 緩慢滾動並檢查是否已到底部
        for scroll_attempt in range(max_scrolls):
            # 獲取當前評論數量
            reviews = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")
            current_review_count = len(reviews)
            
            # 如果連續三次滾動後評論數量沒變，可能已到底部
            if current_review_count == last_review_count:
                unchanged_count += 1
                if unchanged_count >= 3:
                    self.logger.info(f"已載入所有評論: {current_review_count} 條 (連續 {unchanged_count} 次未變化)")
                    break
            else:
                unchanged_count = 0
                
            last_review_count = current_review_count
            self.logger.info(f"當前已加載 {current_review_count} 條評論 (滾動次數: {scroll_attempt + 1}/{max_scrolls})")
            
            # 計算滾動距離 (模擬人類不規則滾動)
            scroll_distance = random.randint(300, 800)
            current_position += scroll_distance
            
            # 執行滾動
            driver.execute_script(f"arguments[0].scrollTop = {current_position};", review_container)
            
            # 隨機點擊一下空白處來確保焦點在頁面上
            if random.random() < 0.2:  # 20%機率
                try:
                    driver.execute_script("arguments[0].click();", review_container)
                except:
                    pass
            
            # 模擬人類閱讀行為的暫停
            pause_time = random.uniform(1.5, 4.5)
            time.sleep(pause_time)