#!/usr/bin/env python3
"""
内存价格监控系统 - 主程序入口
数据来源: 闪存市场 CFM (https://www.chinaflashmarket.com)
"""
import argparse
import sys
from datetime import datetime

from src.scraper import CFMScraper
from src.price_tracker import PriceTracker
from src.report import ReportGenerator
from src.email_sender import EmailSender


def run_monitor(send_email: bool = True, verbose: bool = False):
    """
    运行价格监控
    
    Args:
        send_email: 是否发送邮件
        verbose: 是否输出详细信息
    """
    print(f"\n{'='*50}")
    print(f"📊 内存价格监控系统")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📡 数据来源: 闪存市场 CFM")
    print(f"{'='*50}\n")

    # 1. 爬取价格
    print("🔍 正在获取闪存市场价格数据...")
    scraper = CFMScraper()
    try:
        current_prices = scraper.fetch_all_prices()
    except Exception as e:
        print(f"❌ 获取价格失败: {e}")
        sys.exit(1)

    if not current_prices:
        print("❌ 未获取到任何价格数据")
        sys.exit(1)

    # 2. 分析价格变化
    print("\n📈 正在分析价格变化...")
    tracker = PriceTracker()
    change_data = tracker.update_prices(current_prices)

    total = change_data.get("total_products", 0)
    ups = len(change_data.get("price_ups", []))
    downs = len(change_data.get("price_downs", []))
    
    print(f"   监控产品: {total} 个")
    print(f"   本周上涨: {ups} 个")
    print(f"   本周下跌: {downs} 个\n")

    # 显示变化详情
    if verbose:
        print("📝 价格详情:")
        for item in change_data.get("all_products", []):
            change = item.get("change", 0)
            change_percent = item.get("change_percent", 0)
            
            if change > 0:
                trend = f"↑ +${change:.2f} (+{change_percent:.2f}%)"
            elif change < 0:
                trend = f"↓ ${change:.2f} ({change_percent:.2f}%)"
            else:
                trend = "持平"
            
            print(f"   {item['product']}: ${item['price']:.2f} {trend}")
        print()

    # 3. 生成报告
    print("📄 正在生成报告...")
    generator = ReportGenerator()
    html_report = generator.generate_html(change_data)
    text_report = generator.generate_text(change_data)
    print("✅ 报告生成完成\n")

    # 4. 发送邮件
    if send_email:
        print("📧 正在发送邮件...")
        sender = EmailSender()
        success = sender.send_price_report(html_report, text_report)
        if success:
            print("✅ 邮件发送成功!\n")
        else:
            print("❌ 邮件发送失败\n")
            sys.exit(1)
    else:
        print("⏭️ 跳过邮件发送（--no-email）\n")
        # 输出纯文本报告
        print(text_report)

    print(f"{'='*50}")
    print("🎉 监控任务完成!")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(
        description="内存价格监控系统 - 数据来源: 闪存市场 CFM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 运行监控并发送邮件
  python main.py --no-email   # 运行监控但不发送邮件
  python main.py -v           # 显示详细信息
  
环境变量:
  SMTP_EMAIL      发件邮箱地址
  SMTP_PASSWORD   邮箱授权码（QQ邮箱需要在设置中生成）
  RECIPIENT_EMAIL 收件邮箱（默认: 289997689@qq.com）
  
数据来源:
  闪存市场 CFM: https://www.chinaflashmarket.com/pricecenter/ddrchannel
  价格为渠道市场美元报价，每周二 11:00 (GMT+8) 更新
        """
    )
    
    parser.add_argument(
        "--no-email",
        action="store_true",
        help="不发送邮件，仅在控制台输出报告"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )

    args = parser.parse_args()
    
    run_monitor(
        send_email=not args.no_email,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()
