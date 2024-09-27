
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

class EmailSender:
    """用于发送电子邮件的类。

    Attributes:
        smtp_server: SMTP 服务器地址。
        smtp_port: SMTP 服务器端口。
        username: 发件人邮箱用户名。
        password: 发件人邮箱密码或应用专用密码。
    """

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """初始化 EmailSender 实例。

        Args:
            smtp_server: SMTP 服务器地址。
            smtp_port: SMTP 服务器端口。
            username: 发件人邮箱用户名。
            password: 发件人邮箱密码或应用专用密码。
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        logging.debug("EmailSender 实例已创建。")

    def send_email(self, subject: str, body: str, to_emails: List[str], attachments: Optional[List[str]] = None) -> None:
        """发送电子邮件。

        Args:
            subject: 邮件主题。
            body: 邮件正文内容（支持 Markdown）。
            to_emails: 收件人邮箱列表。
            attachments: 附件文件路径列表。

        Raises:
            Exception: 发送邮件失败时抛出异常。
        """
        # 创建邮件对象
        message = MIMEMultipart()
        message['From'] = self.username
        message['To'] = ", ".join(to_emails)
        message['Subject'] = subject

        # 添加邮件正文
        message.attach(MIMEText(body, 'plain', 'utf-8'))

        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as file:
                        part = MIMEText(file.read(), 'base64', 'utf-8')
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(filepath)}"'
                        message.attach(part)
                except Exception as e:
                    logging.error(f"附件 {filepath} 添加失败: {e}")

        # 发送邮件
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # 开启 TLS 加密
                server.login(self.username, self.password)  # 登录邮箱
                server.sendmail(self.username, to_emails, message.as_string())
                logging.info(f"邮件已成功发送至: {to_emails}")
        except smtplib.SMTPException as e:
            logging.error(f"发送邮件时出错: {e}")
            raise