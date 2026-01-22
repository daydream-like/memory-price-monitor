"""
配置管理模块
"""
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
PRODUCTS_FILE = DATA_DIR / "products.json"
PRICES_FILE = DATA_DIR / "prices.json"

# 邮件配置 (从环境变量读取)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")  # QQ邮箱授权码
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "289997689@qq.com")

# 爬虫配置
REQUEST_TIMEOUT = 10
REQUEST_DELAY = (1, 3)  # 请求间隔范围(秒)
MAX_RETRIES = 3

# 京东API
JD_PRICE_API = "https://p.3.cn/prices/mgets"
JD_PRODUCT_URL = "https://item.jd.com/{sku}.html"
