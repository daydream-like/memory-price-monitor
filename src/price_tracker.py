"""
价格追踪和变化检测模块
"""
import json
from datetime import datetime
from typing import Optional

from .config import PRICES_FILE


class PriceTracker:
    """价格追踪器"""

    def __init__(self):
        self.history = self._load_history()

    def _load_history(self) -> dict:
        """加载历史价格数据"""
        try:
            with open(PRICES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"records": [], "last_prices": {}}

    def _save_history(self):
        """保存历史价格数据"""
        PRICES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PRICES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def update_prices(self, current_data: dict) -> dict:
        """
        更新价格并返回变化信息
        
        Args:
            current_data: 当前价格数据 {category: {update_time, products: [...]}}
            
        Returns:
            变化信息
        """
        today = datetime.now().strftime("%Y-%m-%d")
        last_prices = self.history.get("last_prices", {})
        
        all_products = []
        new_last_prices = {}
        
        # 收集所有产品数据
        for category, cat_data in current_data.items():
            update_time = cat_data.get("update_time", "")
            source = cat_data.get("source", "")
            source_url = cat_data.get("url", "")
            
            for product in cat_data.get("products", []):
                product_name = product.get("product", "")
                price = product.get("price")
                
                if price is None:
                    continue
                
                product_data = {
                    "product": product_name,
                    "category": category,
                    "price": price,
                    "change": product.get("change", 0),
                    "change_percent": product.get("change_percent", 0),
                    "last_week_price": product.get("last_week_price"),
                    "week_high": product.get("week_high"),
                    "week_low": product.get("week_low"),
                    "trend": product.get("trend", ""),
                    "update_time": update_time,
                    "source": source,
                    "source_url": source_url,
                }
                all_products.append(product_data)
                
                # 记录当前价格
                new_last_prices[product_name] = price
        
        # 更新历史记录
        record = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "prices": new_last_prices,
        }
        self.history["records"].append(record)
        self.history["last_prices"] = new_last_prices
        
        # 只保留最近30天的详细记录
        if len(self.history["records"]) > 30:
            self.history["records"] = self.history["records"][-30:]
        
        self._save_history()
        
        # 分类涨跌产品
        price_ups = [p for p in all_products if p.get("change", 0) > 0]
        price_downs = [p for p in all_products if p.get("change", 0) < 0]
        
        return {
            "date": today,
            "all_products": all_products,
            "price_ups": sorted(price_ups, key=lambda x: -x.get("change_percent", 0)),
            "price_downs": sorted(price_downs, key=lambda x: x.get("change_percent", 0)),
            "total_products": len(all_products),
        }

    def get_price_trend(self, product: str, days: int = 7) -> list:
        """获取产品的价格趋势（最近N天）"""
        history = []
        for record in self.history.get("records", [])[-days:]:
            prices = record.get("prices", {})
            if product in prices:
                history.append({
                    "date": record["date"],
                    "price": prices[product],
                })
        return history
