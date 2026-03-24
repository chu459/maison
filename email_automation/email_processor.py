#!/usr/bin/env python3
"""
主邮件处理器
"""

import imaplib
import email
from email import message
from email.header import decode_header
import logging
import time
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import os
from dotenv import load_dotenv
load_dotenv()

from config import load_config, validate_config
from email_classifier import HybridClassifier, ClassificationResult, EmailCategory

logger = logging.getLogger(__name__)

class EmailProcessor:
    """邮件处理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.email_config = config['email']
        self.ai_config = config['ai']
        self.processing_config = config['processing']

        # 初始化分类器
        if self.ai_config.ai_classification_enabled:
            self.classifier = HybridClassifier(self.ai_config.openai_api_key)
        else:
            self.classifier = HybridClassifier(None)

        # 连接状态
        self.imap_connection = None

    def connect(self) -> bool:
        """连接到IMAP服务器"""
        try:
            if self.email_config.use_ssl:
                self.imap_connection = imaplib.IMAP4_SSL(
                    self.email_config.imap_server,
                    self.email_config.imap_port
                )
            else:
                self.imap_connection = imaplib.IMAP4(
                    self.email_config.imap_server,
                    self.email_config.imap_port
                )

            self.imap_connection.login(
                self.email_config.email_address,
                self.email_config.password
            )
            logger.info(f"成功连接到邮箱: {self.email_config.email_address}")
            return True

        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.imap_connection:
            try:
                self.imap_connection.logout()
                logger.info("断开连接")
            except:
                pass
            self.imap_connection = None

    def fetch_unread_emails(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取未读邮件"""
        emails = []

        try:
            # 选择邮箱
            self.imap_connection.select(self.email_config.mailbox)

            # 搜索未读邮件
            status, messages = self.imap_connection.search(None, 'UNSEEN')
            if status != 'OK':
                logger.error("搜索邮件失败")
                return emails

            # 获取邮件ID列表
            email_ids = messages[0].split()
            if not email_ids:
                logger.info("没有未读邮件")
                return emails

            # 限制数量
            email_ids = email_ids[:limit]

            for email_id in email_ids:
                try:
                    # 获取邮件
                    status, msg_data = self.imap_connection.fetch(email_id, '(RFC822)')
                    if status != 'OK':
                        logger.warning(f"获取邮件 {email_id} 失败")
                        continue

                    # 解析邮件
                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    # 提取信息
                    email_info = self._parse_email(msg, email_id)
                    emails.append(email_info)

                except Exception as e:
                    logger.error(f"处理邮件 {email_id} 时出错: {e}")

        except Exception as e:
            logger.error(f"获取未读邮件失败: {e}")

        return emails

    def _parse_email(self, msg: message.Message, email_id: bytes) -> Dict[str, Any]:
        """解析邮件内容"""
        # 解码主题
        subject, encoding = decode_header(msg['Subject'])[0] if msg['Subject'] else ('', None)
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else 'utf-8', errors='ignore')
        elif subject is None:
            subject = ''

        # 发件人
        from_addr = msg['From'] or ''

        # 收件人
        to_addr = msg['To'] or ''

        # 日期
        date_str = msg['Date'] or ''

        # 提取正文
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get('Content-Disposition'))

                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    try:
                        body_bytes = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body = body_bytes.decode(charset, errors='ignore')
                        break
                    except:
                        continue
        else:
            content_type = msg.get_content_type()
            if content_type == 'text/plain':
                try:
                    body_bytes = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    body = body_bytes.decode(charset, errors='ignore')
                except:
                    body = ''

        return {
            'id': email_id.decode(),
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date_str,
            'body_preview': body[:1000],  # 只取前1000字符用于分类
            'body_full': body,
            'raw_message': msg
        }

    def process_email(self, email_info: Dict[str, Any]) -> Dict[str, Any]:
        """处理单封邮件"""
        # 分类
        classification = self.classifier.classify(
            email_info['subject'],
            email_info['body_preview'],
            email_info['from']
        )

        # 记录分类结果
        logger.info(f"邮件分类: {email_info['subject'][:50]}... -> {classification.category.value} (置信度: {classification.confidence:.2f})")

        # 根据分类采取行动
        actions = self._take_actions(email_info, classification)

        return {
            'email_id': email_info['id'],
            'subject': email_info['subject'],
            'from': email_info['from'],
            'classification': classification.to_dict(),
            'actions_taken': actions,
            'processed_at': datetime.now().isoformat()
        }

    def _take_actions(self, email_info: Dict[str, Any], classification: ClassificationResult) -> List[str]:
        """根据分类执行操作"""
        actions = []

        try:
            email_id = email_info['id'].encode()

            # 标记为已读
            self.imap_connection.store(email_id, '+FLAGS', '\\Seen')
            actions.append('marked_read')

            # 根据分类移动邮件
            if classification.category == EmailCategory.SPAM:
                # 移动到垃圾邮件文件夹
                if self._move_email(email_id, self.processing_config.spam_folder):
                    actions.append(f'moved_to_spam')
            elif classification.category == EmailCategory.AUTO_REPLY:
                # 存档或删除
                if self.processing_config.archive_processed:
                    if self._move_email(email_id, self.processing_config.archive_folder):
                        actions.append(f'moved_to_archive')
            elif classification.category == EmailCategory.NEWSLETTER:
                # 可存档或保留
                if self.processing_config.archive_processed:
                    if self._move_email(email_id, self.processing_config.archive_folder):
                        actions.append(f'moved_to_archive')
            elif classification.category == EmailCategory.URGENT:
                # 重要邮件，保持原位，可以添加标签
                self.imap_connection.store(email_id, '+FLAGS', '\\Flagged')
                actions.append('flagged')
            elif classification.category == EmailCategory.IMPORTANT:
                # 标记重要
                self.imap_connection.store(email_id, '+FLAGS', '\\Flagged')
                actions.append('flagged')

            # 自动回复（如果启用）
            if self.processing_config.auto_reply_enabled and classification.category not in [EmailCategory.SPAM, EmailCategory.AUTO_REPLY, EmailCategory.NEWSLETTER]:
                # 这里可以实现自动回复逻辑
                # 需要SMTP连接，暂时跳过
                pass

        except Exception as e:
            logger.error(f"执行操作时出错: {e}")
            actions.append(f'error: {str(e)}')

        return actions

    def _move_email(self, email_id: bytes, folder: str) -> bool:
        """移动邮件到指定文件夹"""
        try:
            # 检查文件夹是否存在，不存在则创建
            status, folders = self.imap_connection.list()
            folder_exists = any(folder.encode() in f for f in folders)

            if not folder_exists:
                # 创建文件夹
                self.imap_connection.create(folder)

            # 复制邮件到新文件夹
            self.imap_connection.copy(email_id, folder)

            # 在原邮箱中删除
            self.imap_connection.store(email_id, '+FLAGS', '\\Deleted')

            return True
        except Exception as e:
            logger.error(f"移动邮件失败: {e}")
            return False

    def run_once(self) -> List[Dict[str, Any]]:
        """运行一次处理"""
        results = []

        if not self.connect():
            logger.error("无法连接到邮箱")
            return results

        try:
            # 获取未读邮件
            emails = self.fetch_unread_emails(self.processing_config.max_emails_per_check)
            logger.info(f"找到 {len(emails)} 封未读邮件")

            # 处理每封邮件
            for email_info in emails:
                try:
                    result = self.process_email(email_info)
                    results.append(result)
                except Exception as e:
                    logger.error(f"处理邮件 {email_info.get('id')} 失败: {e}")

            # 提交删除操作
            self.imap_connection.expunge()

        finally:
            self.disconnect()

        return results

    def run_continuous(self):
        """持续运行处理"""
        logger.info(f"开始持续处理，检查间隔: {self.processing_config.check_interval_minutes} 分钟")

        while True:
            try:
                logger.info("开始检查邮件...")
                results = self.run_once()

                if results:
                    logger.info(f"处理完成: {len(results)} 封邮件")
                    # 保存处理结果
                    self._save_results(results)

                # 等待下次检查
                time.sleep(self.processing_config.check_interval_minutes * 60)

            except KeyboardInterrupt:
                logger.info("用户中断")
                break
            except Exception as e:
                logger.error(f"运行出错: {e}")
                time.sleep(60)  # 出错后等待1分钟

    def _save_results(self, results: List[Dict[str, Any]]):
        """保存处理结果"""
        try:
            filename = f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"结果保存到: {filename}")
        except Exception as e:
            logger.error(f"保存结果失败: {e}")

def setup_logging(logging_config):
    """设置日志"""
    handlers = []

    if logging_config.enable_console_log:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, logging_config.log_level))
        handlers.append(console_handler)

    if logging_config.log_file:
        file_handler = logging.FileHandler(logging_config.log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, logging_config.log_level))
        handlers.append(file_handler)

    logging.basicConfig(
        level=getattr(logging, logging_config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

def main():
    """主函数"""
    # 加载配置
    config = load_config()

    try:
        validate_config(config)
    except ValueError as e:
        logger.error(e)
        print(f"配置错误: {e}")
        print("请设置必要的环境变量:")
        print("  EMAIL_ADDRESS=你的邮箱")
        print("  EMAIL_PASSWORD=邮箱密码或应用专用密码")
        print("  OPENAI_API_KEY=你的OpenAI API密钥（可选）")
        return

    # 设置日志
    setup_logging(config['logging'])

    # 创建处理器
    processor = EmailProcessor(config)

    # 运行一次处理
    print("开始邮件处理...")
    results = processor.run_once()

    if results:
        print(f"处理完成: {len(results)} 封邮件")
        for result in results:
            print(f"  - {result['subject'][:50]}... -> {result['classification']['category']}")
    else:
        print("没有需要处理的邮件")

if __name__ == "__main__":
    main()