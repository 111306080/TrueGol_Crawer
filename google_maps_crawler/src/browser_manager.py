#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import random
import logging

class BrowserManager:
    def __init__(self):
        self.logger = logging.getLogger("BrowserManager")
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
        ]
        
    def create_browser(self, headless=False):
        """創建並配置瀏覽器實例"""
        options = Options()
        
        if headless:
            options.add_argument("--headless")
        
        # 隨機選擇一個 User-Agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"user-agent={user_agent}")
        
        # 設置語言為英文
        options.add_argument("--lang=en-US")
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en',
            'profile.default_content_setting_values.geolocation': 1,  # Allow geolocation
            'profile.default_content_setting_values.notifications': 2  # Block notifications
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
        options.add_argument("--disable-notifications")  # 禁用通知
        options.add_argument("--disable-popup-blocking")  # 允許彈出窗口
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 隱藏 WebDriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 設置語言相關的 JavaScript 屬性
        driver.execute_script("""
            Object.defineProperty(navigator, 'language', {
                get: function() { return 'en-US'; }
            });
            Object.defineProperty(navigator, 'languages', {
                get: function() { return ['en-US', 'en']; }
            });
        """)
        
        self.logger.info(f"已創建瀏覽器實例 (User-Agent: {user_agent[:30]}...)")
        self.logger.info(f"瀏覽器語言設置: en-US")
        
        return driver
    
    def close_browser(self, driver):
        """安全關閉瀏覽器"""
        if driver:
            try:
                driver.quit()
                self.logger.info("瀏覽器已安全關閉")
            except Exception as e:
                self.logger.error(f"關閉瀏覽器時出錯: {str(e)}")