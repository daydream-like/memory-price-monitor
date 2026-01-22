# 京东内存/SSD 价格监控系统

自动监控京东平台上内存、SSD等存储产品的价格变化，每天定时发送报告到指定邮箱。

## 功能特点

- 🔍 **自动爬取** - 自动获取京东商品实时价格
- 📊 **价格追踪** - 记录历史价格，检测涨跌变化
- 📧 **邮件报告** - 生成美观的HTML报告并发送邮件
- ⏰ **定时运行** - 通过 GitHub Actions 每天自动运行
- 🏷️ **新低提醒** - 标记历史最低价商品

## 监控商品

默认监控以下品类：
- DDR5 内存条（三星、美光、金士顿、芝奇、海盗船）
- 消费级 NVMe SSD（三星、美光、西数、SK海力士）
- 企业级存储（三星、美光数据中心级SSD）

## 快速开始

### 方式一：GitHub Actions（推荐）

1. **Fork 本仓库** 到你的 GitHub 账号

2. **配置 Secrets**
   
   进入仓库 Settings → Secrets and variables → Actions，添加以下 Secrets：
   
   | Secret 名称 | 说明 | 示例 |
   |------------|------|------|
   | `SMTP_EMAIL` | 发件邮箱地址 | `your_email@qq.com` |
   | `SMTP_PASSWORD` | 邮箱授权码 | QQ邮箱需在设置中生成 |
   | `RECIPIENT_EMAIL` | 收件邮箱 | `289997689@qq.com` |

3. **启用 Actions**
   
   进入 Actions 页面，启用 Workflows

4. **手动测试**
   
   点击 "价格监控" workflow → "Run workflow" 手动触发一次

### 方式二：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/price-monitor.git
cd price-monitor

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export SMTP_EMAIL="your_email@qq.com"
export SMTP_PASSWORD="your_auth_code"
export RECIPIENT_EMAIL="289997689@qq.com"

# 4. 运行
python main.py
```

## 命令行参数

```bash
python main.py              # 运行监控并发送邮件
python main.py --no-email   # 运行监控但不发送邮件（仅控制台输出）
python main.py -v           # 显示详细信息
```

## 添加/修改监控商品

编辑 `data/products.json` 文件：

```json
{
  "categories": {
    "分类名称": {
      "description": "分类描述",
      "products": [
        {
          "sku": "京东商品SKU",
          "name": "商品名称",
          "brand": "品牌"
        }
      ]
    }
  }
}
```

**如何获取京东 SKU：**
- 打开京东商品页面
- 从 URL 中获取数字，如 `https://item.jd.com/100012016578.html` 的 SKU 是 `100012016578`

## QQ 邮箱授权码获取

1. 登录 QQ 邮箱网页版
2. 进入 设置 → 账户
3. 找到 "POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
4. 开启 "POP3/SMTP服务"
5. 按提示获取授权码

## 项目结构

```
price-monitor/
├── src/
│   ├── config.py        # 配置管理
│   ├── scraper.py       # 京东价格爬取
│   ├── price_tracker.py # 价格追踪
│   ├── report.py        # 报告生成
│   └── email_sender.py  # 邮件发送
├── data/
│   ├── products.json    # 监控商品配置
│   └── prices.json      # 历史价格数据
├── templates/
│   └── email.html       # 邮件HTML模板
├── .github/
│   └── workflows/
│       └── monitor.yml  # GitHub Actions配置
├── main.py              # 主程序入口
├── requirements.txt     # Python依赖
└── README.md
```

## 注意事项

- 京东价格接口可能随时变化，如遇问题请提 Issue
- GitHub Actions 免费版每月 2000 分钟，每天运行约 1 分钟，完全够用
- 建议使用 QQ 邮箱，国内访问稳定

## License

MIT
