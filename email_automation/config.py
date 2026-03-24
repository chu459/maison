#!/usr/bin/env python3
"""
配置文件
从环境变量或配置文件读取配置
"""

import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class EmailConfig:
    """邮箱配置"""
    imap_server: str
    imap_port: int
    email_address: str
    password: str  # 或应用专用密码
    use_ssl: bool = True
    mailbox: str = "INBOX"

@dataclass
class AIConfig:
    """AI配置"""
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    ai_classification_enabled: bool = False
    ai_min_confidence_threshold: float = 0.7

@dataclass
class ProcessingConfig:
    """处理配置"""
    check_interval_minutes: int = 5
    max_emails_per_check: int = 50
    archive_processed: bool = True
    archive_folder: str = "Processed"
    spam_folder: str = "Spam"
    auto_reply_enabled: bool = False
    auto_reply_template: str = "感谢您的邮件。我们已收到并会尽快处理。"

@dataclass
class LoggingConfig:
    """日志配置"""
    log_level: str = "INFO"
    log_file: Optional[str] = "email_automation.log"
    enable_console_log: bool = True

def load_config():
    """从环境变量加载配置"""
    # 邮箱配置
    email_config = EmailConfig(
        imap_server=os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com"),
        imap_port=int(os.getenv("EMAIL_IMAP_PORT", "993")),
        email_address=os.getenv("EMAIL_ADDRESS", ""),
        password=os.getenv("EMAIL_PASSWORD", ""),
        use_ssl=os.getenv("EMAIL_USE_SSL", "true").lower() == "true",
        mailbox=os.getenv("EMAIL_MAILBOX", "INBOX")
    )

    # AI配置
    ai_config = AIConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        ai_classification_enabled=os.getenv("AI_CLASSIFICATION_ENABLED", "false").lower() == "true",
        ai_min_confidence_threshold=float(os.getenv("AI_MIN_CONFIDENCE_THRESHOLD", "0.7"))
    )

    # 处理配置
    processing_config = ProcessingConfig(
        check_interval_minutes=int(os.getenv("CHECK_INTERVAL_MINUTES", "5")),
        max_emails_per_check=int(os.getenv("MAX_EMAILS_PER_CHECK", "50")),
        archive_processed=os.getenv("ARCHIVE_PROCESSED", "true").lower() == "true",
        archive_folder=os.getenv("ARCHIVE_FOLDER", "Processed"),
        spam_folder=os.getenv("SPAM_FOLDER", "Spam"),
        auto_reply_enabled=os.getenv("AUTO_REPLY_ENABLED", "false").lower() == "true",
        auto_reply_template=os.getenv("AUTO_REPLY_TEMPLATE", "感谢您的邮件。我们已收到并会尽快处理。")
    )

    # 日志配置
    logging_config = LoggingConfig(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_file=os.getenv("LOG_FILE", "email_automation.log"),
        enable_console_log=os.getenv("ENABLE_CONSOLE_LOG", "true").lower() == "true"
    )

    return {
        'email': email_config,
        'ai': ai_config,
        'processing': processing_config,
        'logging': logging_config
    }

def validate_config(config):
    """验证配置"""
    errors = []

    email = config['email']
    if not email.email_address:
        errors.append("EMAIL_ADDRESS未设置")
    if not email.password:
        errors.append("EMAIL_PASSWORD未设置")

    ai = config['ai']
    if ai.ai_classification_enabled and not ai.openai_api_key:
        errors.append("AI分类已启用但OPENAI_API_KEY未设置")

    if errors:
        raise ValueError(f"配置错误: {', '.join(errors)}")

    return True

if __name__ == "__main__":
    # 测试配置加载
    config = load_config()
    print("配置加载成功:")
    print(f"邮箱: {config['email'].email_address}")
    print(f"IMAP服务器: {config['email'].imap_server}")
    print(f"AI分类启用: {config['ai'].ai_classification_enabled}")
    print(f"检查间隔: {config['processing'].check_interval_minutes}分钟")