# Google Maps 餐廳爬蟲

Google Maps 餐廳評論自動爬蟲工具。

## 初次設置

1. 創建必要目錄：
```bash
mkdir -p data/raw data/processed logs
touch data/raw/.gitkeep data/processed/.gitkeep logs/.gitkeep
```

2. 安裝套件：
```bash
pip install -r requirements.txt
```

## 重要：避免重複爬取

修改 `main.py` 中的餐廳類型來避免重複爬取：


## 執行

```bash
python main.py
```

## 輸出

- 原始數據：`data/raw/`
- 整合後數據：`data/processed/restaurant_dataset.json`
- 爬蟲日誌：`logs/crawler.log`

## 注意事項

- 爬蟲有隨機延遲和休息時間，避免被偵測
- 如果中斷，會從上次進度繼續爬取（進度存在 `data/raw/progress.json`）
