"""
闪存市场价格爬虫模块
数据来源: https://www.chinaflashmarket.com
"""
import json
import re
import time
from typing import Optional
from datetime import datetime

import requests
from fake_useragent import UserAgent

from .config import (
    MAX_RETRIES,
    REQUEST_TIMEOUT,
)


class CFMScraper:
    """闪存市场价格爬虫"""

    # 数据源URL
    URLS = {
        "ddr_channel": "https://www.chinaflashmarket.com/pricecenter/ddrchannel",
    }

    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self._update_headers()

    def _update_headers(self):
        """更新请求头"""
        self.session.headers.update({
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.chinaflashmarket.com/",
            "Cache-Control": "no-cache",
        })

    def _parse_html_table(self, html: str) -> list:
        """解析HTML表格"""
        results = []
        
        # 查找表格内容
        # 使用更宽松的正则表达式
        table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            print("未找到表格")
            return results
        
        table_html = table_match.group(1)
        
        # 提取所有行
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
        
        for row in rows:
            # 跳过表头
            if '<th' in row.lower():
                continue
            
            # 提取单元格
            cells = re.findall(r'<(?:td|rowheader)[^>]*>(.*?)</(?:td|rowheader)>', row, re.DOTALL | re.IGNORECASE)
            
            if len(cells) >= 7:
                # 提取产品名称（从链接中）
                product_match = re.search(r'>([^<]+)</a>', cells[0])
                if not product_match:
                    continue
                product = product_match.group(1).strip()
                
                # 提取数字
                try:
                    price = float(re.search(r'\$([\d.]+)', cells[1]).group(1))
                    change_match = re.search(r'([+-]?[\d.]+)', cells[2])
                    change = float(change_match.group(1)) if change_match else 0
                    change_pct_match = re.search(r'([+-]?[\d.]+)%', cells[3])
                    change_pct = float(change_pct_match.group(1)) if change_pct_match else 0
                    last_price = float(re.search(r'\$([\d.]+)', cells[4]).group(1))
                    week_high = float(re.search(r'\$([\d.]+)', cells[5]).group(1))
                    week_low = float(re.search(r'\$([\d.]+)', cells[6]).group(1))
                    
                    # 判断涨跌方向
                    if '+' in cells[2]:
                        change = abs(change)
                        change_pct = abs(change_pct)
                        trend = "up"
                    else:
                        change = -abs(change) if change != 0 else 0
                        change_pct = -abs(change_pct) if change_pct != 0 else 0
                        trend = "down" if change < 0 else "flat"
                    
                    results.append({
                        "product": product,
                        "price": price,
                        "change": change,
                        "change_percent": change_pct,
                        "last_week_price": last_price,
                        "week_high": week_high,
                        "week_low": week_low,
                        "trend": trend,
                    })
                except (AttributeError, ValueError) as e:
                    print(f"解析数据失败: {e}")
                    continue
        
        return results

    def fetch_ddr_channel(self) -> dict:
        """获取内存条渠道市场价格"""
        url = self.URLS["ddr_channel"]
        
        for attempt in range(MAX_RETRIES):
            try:
                self._update_headers()
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                response.encoding = 'utf-8'
                html = response.text
                
                # 检查是否获取到有效内容
                if 'DDR' not in html:
                    print(f"页面内容可能不正确 (尝试 {attempt + 1})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(2)
                        continue
                
                # 提取更新时间
                time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})', html)
                update_time = time_match.group(1) if time_match else datetime.now().strftime("%Y-%m-%d %H:%M")
                
                # 解析价格表格
                products = self._parse_html_table(html)
                
                if products:
                    return {
                        "update_time": update_time,
                        "currency": "USD",
                        "source": "闪存市场 CFM",
                        "url": url,
                        "products": products,
                    }
                
            except requests.RequestException as e:
                print(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        
        # 如果爬取失败，返回最新的已知数据（基于2026-01-20的数据）
        print("⚠️ 使用缓存数据（闪存市场可能有访问限制）")
        return self._get_cached_data()

    def _get_cached_data(self) -> dict:
        """返回缓存的最新数据"""
        return {
            "update_time": "2026-01-20 11:00",
            "currency": "USD",
            "source": "闪存市场 CFM (缓存)",
            "url": "https://www.chinaflashmarket.com/pricecenter/ddrchannel",
            "products": [
                {"product": "DDR4 UDIMM 8GB 3200", "price": 47.00, "change": 2.00, "change_percent": 4.44, "last_week_price": 45.00, "week_high": 52.00, "week_low": 45.00, "trend": "up"},
                {"product": "DDR4 UDIMM 16GB 3200", "price": 90.00, "change": 5.00, "change_percent": 5.88, "last_week_price": 85.00, "week_high": 100.60, "week_low": 89.00, "trend": "up"},
                {"product": "DDR4 UDIMM 32GB 3200", "price": 160.00, "change": 20.00, "change_percent": 14.29, "last_week_price": 140.00, "week_high": 170.00, "week_low": 155.00, "trend": "up"},
                {"product": "DDR5 UDIMM 16GB 5600", "price": 160.00, "change": 35.00, "change_percent": 28.00, "last_week_price": 125.00, "week_high": 162.00, "week_low": 158.00, "trend": "up"},
                {"product": "DDR5 UDIMM 16GB 6000", "price": 170.00, "change": 25.00, "change_percent": 17.24, "last_week_price": 145.00, "week_high": 172.00, "week_low": 167.00, "trend": "up"},
                {"product": "DDR5 UDIMM 32GB 5600", "price": 260.00, "change": 30.00, "change_percent": 13.04, "last_week_price": 230.00, "week_high": 263.00, "week_low": 257.00, "trend": "up"},
                {"product": "DDR5 UDIMM 32GB 6000", "price": 270.00, "change": 20.00, "change_percent": 8.00, "last_week_price": 250.00, "week_high": 273.00, "week_low": 267.00, "trend": "up"},
            ],
        }

    def fetch_all_prices(self) -> dict:
        """获取所有价格数据"""
        results = {}
        
        print("🔍 正在获取闪存市场价格数据...")
        
        # 获取内存条渠道价格
        ddr_data = self.fetch_ddr_channel()
        if ddr_data.get("products"):
            results["内存条(渠道市场)"] = ddr_data
            print(f"✅ 获取到 {len(ddr_data['products'])} 个内存产品价格")
        else:
            print("❌ 获取内存价格失败")
        
        return results


# 为了兼容性
JDScraper = CFMScraper


def main():
    """测试爬虫"""
    scraper = CFMScraper()
    results = scraper.fetch_all_prices()
    
    for category, data in results.items():
        print(f"\n=== {category} ===")
        print(f"更新时间: {data.get('update_time')}")
        print(f"数据来源: {data.get('source')}")
        for product in data.get("products", []):
            trend = "↑" if product.get("trend") == "up" else "↓" if product.get("trend") == "down" else "-"
            print(f"  {product['product']}: ${product['price']:.2f} {trend}{abs(product.get('change_percent', 0)):.2f}%")


if __name__ == "__main__":
    main()
