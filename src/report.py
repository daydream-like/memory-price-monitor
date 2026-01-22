"""
报告生成模块
"""
import random
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import PROJECT_ROOT


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        template_dir = PROJECT_ROOT / "templates"
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def _generate_trend_heights(self, current_price: float, change_percent: float) -> list:
        """
        生成走势图高度数据（模拟6周走势）
        
        基于当前价格和涨跌幅度反推历史走势
        """
        heights = []
        base_height = 25  # 基准高度
        
        # 根据涨跌幅度计算历史价格趋势
        # 假设涨幅越大，之前的价格越低
        if change_percent > 0:
            # 上涨趋势：从低到高
            for i in range(6):
                factor = 0.6 + (i * 0.08)  # 逐渐增加
                height = int(base_height * factor)
                heights.append(min(30, max(8, height)))
        elif change_percent < 0:
            # 下跌趋势：从高到低
            for i in range(6):
                factor = 1.0 - (i * 0.06)  # 逐渐减少
                height = int(base_height * factor)
                heights.append(min(30, max(8, height)))
        else:
            # 持平
            heights = [20, 20, 20, 20, 20, 20]
        
        return heights

    def generate_html(self, data: dict) -> str:
        """
        生成HTML报告
        
        Args:
            data: 价格数据
            
        Returns:
            HTML字符串
        """
        template = self.env.get_template("email.html")
        
        all_products = data.get("all_products", [])
        price_ups = [p for p in all_products if p.get("change", 0) > 0]
        price_downs = [p for p in all_products if p.get("change", 0) < 0]
        
        # 计算平均涨幅
        if all_products:
            avg_change = sum(p.get("change_percent", 0) for p in all_products) / len(all_products)
        else:
            avg_change = 0
        
        # 获取数据更新时间
        data_update_time = "2026-01-20 11:00"
        for p in all_products:
            if p.get("update_time"):
                data_update_time = p.get("update_time")
                break
        
        # 按涨幅排序并添加排名和走势图数据
        all_products_ranked = sorted(all_products, key=lambda x: -x.get("change_percent", 0))
        for i, product in enumerate(all_products_ranked):
            product["rank"] = i + 1
            product["trend_heights"] = self._generate_trend_heights(
                product.get("price", 0),
                product.get("change_percent", 0)
            )
        
        # 选择热门产品（DDR5优先展示）
        top_products = []
        ddr5_products = [p for p in all_products if "DDR5" in p.get("product", "")]
        ddr4_products = [p for p in all_products if "DDR4" in p.get("product", "")]
        
        # 选择DDR5 32GB和16GB各一个，DDR4 16GB一个
        for p in ddr5_products:
            if "32GB" in p.get("product", "") and len(top_products) < 4:
                top_products.append(p)
                break
        for p in ddr5_products:
            if "16GB" in p.get("product", "") and p not in top_products and len(top_products) < 4:
                top_products.append(p)
                break
        for p in ddr4_products:
            if "16GB" in p.get("product", "") and len(top_products) < 4:
                top_products.append(p)
                break
        for p in ddr4_products:
            if "32GB" in p.get("product", "") and len(top_products) < 4:
                top_products.append(p)
                break
        
        # 渲染模板
        html = template.render(
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            data_update_time=data_update_time,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_products=len(all_products),
            price_ups=len(price_ups),
            price_downs=len(price_downs),
            avg_change=avg_change,
            all_products=all_products,
            all_products_ranked=all_products_ranked,
            top_products=top_products,
        )
        
        return html

    def generate_text(self, data: dict) -> str:
        """
        生成纯文本报告（作为备用）
        """
        all_products = data.get("all_products", [])
        price_ups = [p for p in all_products if p.get("change", 0) > 0]
        price_downs = [p for p in all_products if p.get("change", 0) < 0]
        
        # 获取数据更新时间
        data_update_time = "2026-01-20 11:00"
        for p in all_products:
            if p.get("update_time"):
                data_update_time = p.get("update_time")
                break
        
        lines = [
            f"📊 内存价格监控报告 - {data.get('date', '')}",
            "=" * 55,
            f"📅 数据更新时间: {data_update_time}",
            "",
            "📈 市场概览:",
            f"   监控产品: {len(all_products)} 个",
            f"   本周上涨: {len(price_ups)} 个",
            f"   本周下跌: {len(price_downs)} 个",
            "",
            "💰 热门产品价格:",
            "-" * 55,
        ]
        
        # 显示热门产品
        for item in all_products[:4]:
            change = item.get("change", 0)
            change_percent = item.get("change_percent", 0)
            trend = f"↑+{change_percent:.1f}%" if change > 0 else f"↓{change_percent:.1f}%" if change < 0 else "持平"
            lines.append(f"   {item['product']}: ${item['price']:.2f} ({trend})")
        
        lines.append("")
        lines.append("📊 本周价格变动详情:")
        lines.append("-" * 55)
        
        # 按涨幅排序
        sorted_products = sorted(all_products, key=lambda x: -x.get("change_percent", 0))
        
        for i, item in enumerate(sorted_products, 1):
            change = item.get("change", 0)
            change_percent = item.get("change_percent", 0)
            
            if change > 0:
                trend = f"↑ +${change:.2f} (+{change_percent:.2f}%)"
            elif change < 0:
                trend = f"↓ ${change:.2f} ({change_percent:.2f}%)"
            else:
                trend = "持平"
            
            rank = f"[{i}]" if i <= 3 else f" {i}."
            lines.append(
                f"\n  {rank} {item['product']}\n"
                f"      本周价: ${item['price']:.2f}  {trend}\n"
                f"      上周价: ${item.get('last_week_price', 0):.2f}  "
                f"周高/低: ${item.get('week_low', 0):.2f} ~ ${item.get('week_high', 0):.2f}"
            )
        
        lines.append("")
        lines.append("=" * 55)
        lines.append(f"数据来源: 闪存市场 CFM")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("💡 价格为渠道市场美元报价，每周二 11:00 (GMT+8) 更新")
        
        return "\n".join(lines)
