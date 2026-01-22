"""
邮件发送模块
"""
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import (
    RECIPIENT_EMAIL,
    SMTP_EMAIL,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
)


class EmailSender:
    """邮件发送器"""

    def __init__(
        self,
        smtp_server: str = None,
        smtp_port: int = None,
        email: str = None,
        password: str = None,
    ):
        self.smtp_server = smtp_server or SMTP_SERVER
        self.smtp_port = smtp_port or SMTP_PORT
        self.email = email or SMTP_EMAIL
        self.password = password or SMTP_PASSWORD

    def send(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str = None,
    ) -> bool:
        """
        发送邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选，作为备用）
            
        Returns:
            是否发送成功
        """
        if not self.email or not self.password:
            print("❌ 错误: 未配置SMTP邮箱或授权码")
            print("   请设置环境变量 SMTP_EMAIL 和 SMTP_PASSWORD")
            return False

        try:
            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.email
            msg["To"] = to_email

            # 添加纯文本版本（作为备用）
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                msg.attach(text_part)

            # 添加HTML版本
            html_part = MIMEText(html_content, "html", "utf-8")
            msg.attach(html_part)

            # 发送邮件
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL(
                self.smtp_server, self.smtp_port, context=context
            ) as server:
                server.login(self.email, self.password)
                server.sendmail(self.email, to_email, msg.as_string())

            print(f"✅ 邮件发送成功: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP认证失败，请检查邮箱和授权码")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ SMTP错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 发送邮件时出错: {e}")
            return False

    def send_price_report(self, html_content: str, text_content: str = None) -> bool:
        """
        发送价格报告邮件
        
        Args:
            html_content: HTML报告内容
            text_content: 纯文本报告内容
            
        Returns:
            是否发送成功
        """
        from datetime import datetime
        
        today = datetime.now().strftime("%Y-%m-%d")
        subject = f"📊 内存/SSD 价格监控报告 - {today}"
        
        return self.send(
            to_email=RECIPIENT_EMAIL,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )


def test_email():
    """测试邮件发送"""
    sender = EmailSender()
    
    html = """
    <html>
    <body>
        <h1>测试邮件</h1>
        <p>这是一封测试邮件，用于验证SMTP配置是否正确。</p>
    </body>
    </html>
    """
    
    success = sender.send(
        to_email=RECIPIENT_EMAIL,
        subject="价格监控系统 - 测试邮件",
        html_content=html,
        text_content="这是一封测试邮件",
    )
    
    if success:
        print("测试邮件发送成功！")
    else:
        print("测试邮件发送失败，请检查配置。")


if __name__ == "__main__":
    test_email()
