#!/usr/bin/env python3
"""
邮件分类器模块
支持基于规则和AI的分类
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional
# import openai  # 可选，动态导入

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailCategory(Enum):
    """邮件分类"""
    URGENT = "urgent"       # 紧急，需要立即处理
    IMPORTANT = "important" # 重要，今天内处理
    NORMAL = "normal"       # 普通，本周内处理
    LOW = "low"            # 低优先级，可批量处理
    SPAM = "spam"          # 垃圾邮件
    AUTO_REPLY = "auto_reply" # 自动回复
    NEWSLETTER = "newsletter" # 订阅邮件

class ClassificationResult:
    """分类结果"""
    def __init__(self, category: EmailCategory, confidence: float,
                 subcategories: List[str], suggested_actions: List[str]):
        self.category = category
        self.confidence = confidence  # 0-1
        self.subcategories = subcategories
        self.suggested_actions = suggested_actions

    def to_dict(self):
        return {
            'category': self.category.value,
            'confidence': self.confidence,
            'subcategories': self.subcategories,
            'suggested_actions': self.suggested_actions
        }

class RuleBasedClassifier:
    """基于规则的分类器"""

    def __init__(self):
        # 关键词规则
        self.rules = {
            EmailCategory.URGENT: {
                'keywords': ['urgent', '紧急', 'asap', 'immediately', 'critical', 'critical', 'deadline today', 'today'],
                'subject_patterns': [r'紧急', r'URGENT', r'ASAP'],
                'from_patterns': [r'boss', r'manager', r'ceo', r'领导', r'上级']
            },
            EmailCategory.IMPORTANT: {
                'keywords': ['important', '重要', 'meeting', '会议', 'report', '报告', 'project', '项目'],
                'subject_patterns': [r'重要', r'IMPORTANT', r'会议', r'报告'],
                'from_patterns': [r'team', r'同事', r'客户', r'customer']
            },
            EmailCategory.AUTO_REPLY: {
                'keywords': ['auto reply', '自动回复', 'out of office', 'vacation', '不在办公室'],
                'subject_patterns': [r'自动回复', r'Auto Reply', r'Out of Office'],
                'from_patterns': []
            },
            EmailCategory.NEWSLETTER: {
                'keywords': ['newsletter', '订阅', 'unsubscribe', '退订'],
                'subject_patterns': [r'Newsletter', r'订阅', r'每周更新'],
                'from_patterns': []
            },
            EmailCategory.SPAM: {
                'keywords': ['win', 'free', '恭喜', '中奖', 'discount', '促销', 'click here'],
                'subject_patterns': [r'WIN', r'FREE', r'恭喜', r'中奖'],
                'from_patterns': []
            }
        }

    def classify(self, subject: str, body: str, from_addr: str) -> ClassificationResult:
        """
        基于规则分类邮件
        """
        subject_lower = subject.lower()
        body_lower = body.lower()
        from_lower = from_addr.lower()

        scores = {cat: 0.0 for cat in self.rules.keys()}

        # 应用规则评分
        for category, rule in self.rules.items():
            # 关键词匹配
            for keyword in rule['keywords']:
                if keyword in subject_lower:
                    scores[category] += 2.0
                if keyword in body_lower:
                    scores[category] += 1.0

            # 主题模式匹配
            for pattern in rule['subject_patterns']:
                if re.search(pattern, subject, re.IGNORECASE):
                    scores[category] += 3.0

            # 发件人模式匹配
            for pattern in rule['from_patterns']:
                if re.search(pattern, from_addr, re.IGNORECASE):
                    scores[category] += 2.0

        # 确定最高分
        if not any(scores.values()):
            # 默认分类为普通
            return ClassificationResult(
                category=EmailCategory.NORMAL,
                confidence=0.5,
                subcategories=['general'],
                suggested_actions=['read later']
            )

        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]

        # 归一化置信度
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.5

        # 生成子类别和建议行动
        subcategories = []
        suggested_actions = []

        if max_category == EmailCategory.URGENT:
            subcategories.append('time_sensitive')
            suggested_actions = ['reply immediately', 'forward to manager']
        elif max_category == EmailCategory.IMPORTANT:
            subcategories.append('business_related')
            suggested_actions = ['reply today', 'schedule meeting']
        elif max_category == EmailCategory.AUTO_REPLY:
            subcategories.append('system_generated')
            suggested_actions = ['archive', 'no action needed']
        elif max_category == EmailCategory.NEWSLETTER:
            subcategories.append('subscription')
            suggested_actions = ['read when free', 'unsubscribe if unwanted']
        elif max_category == EmailCategory.SPAM:
            subcategories.append('commercial')
            suggested_actions = ['mark as spam', 'delete']
        else:
            subcategories.append('general')
            suggested_actions = ['read later', 'archive']

        return ClassificationResult(
            category=max_category,
            confidence=confidence,
            subcategories=subcategories,
            suggested_actions=suggested_actions
        )

class AIClassifier:
    """AI分类器（使用OpenAI API）"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        # 动态导入openai，如果不可用则记录警告
        try:
            import openai
            openai.api_key = api_key
            self.openai_available = True
        except ImportError:
            logger.warning("openai模块未安装，AI分类器将不可用")
            self.openai_available = False

    def classify(self, subject: str, body: str, from_addr: str) -> ClassificationResult:
        """
        使用AI分类邮件
        注意：每次分类都有API成本，实际使用时应缓存或批量处理
        """
        prompt = f"""
请对以下邮件进行分类：

发件人: {from_addr}
主题: {subject}
正文（摘要）: {body[:500]}

请从以下类别中选择最合适的一个：
1. urgent - 紧急，需要立即处理
2. important - 重要，今天内处理
3. normal - 普通，本周内处理
4. low - 低优先级，可批量处理
5. spam - 垃圾邮件
6. auto_reply - 自动回复
7. newsletter - 订阅邮件

请用JSON格式回复，包含以下字段：
- category: 类别（小写英文）
- confidence: 置信度（0-1之间）
- reason: 简要理由
- suggested_action: 建议操作

仅返回JSON，不要有其他内容。
"""

        # 检查openai是否可用
        if not self.openai_available:
            logger.warning("openai不可用，降级到规则分类")
            rule_classifier = RuleBasedClassifier()
            return rule_classifier.classify(subject, body, from_addr)

        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的邮件分类助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )

            result_text = response.choices[0].message.content.strip()
            # 解析JSON
            import json
            result = json.loads(result_text)

            # 映射到枚举
            category_map = {
                'urgent': EmailCategory.URGENT,
                'important': EmailCategory.IMPORTANT,
                'normal': EmailCategory.NORMAL,
                'low': EmailCategory.LOW,
                'spam': EmailCategory.SPAM,
                'auto_reply': EmailCategory.AUTO_REPLY,
                'newsletter': EmailCategory.NEWSLETTER
            }

            category = category_map.get(result['category'], EmailCategory.NORMAL)

            return ClassificationResult(
                category=category,
                confidence=result.get('confidence', 0.8),
                subcategories=[result.get('reason', '')],
                suggested_actions=[result.get('suggested_action', '')]
            )

        except Exception as e:
            logger.error(f"AI分类失败: {e}")
            # 降级到规则分类
            rule_classifier = RuleBasedClassifier()
            return rule_classifier.classify(subject, body, from_addr)

class HybridClassifier:
    """混合分类器：先尝试规则，如果置信度低则使用AI"""

    def __init__(self, ai_api_key: Optional[str] = None):
        self.rule_classifier = RuleBasedClassifier()
        self.ai_classifier = None
        if ai_api_key:
            self.ai_classifier = AIClassifier(ai_api_key)

    def classify(self, subject: str, body: str, from_addr: str) -> ClassificationResult:
        # 先使用规则分类
        rule_result = self.rule_classifier.classify(subject, body, from_addr)

        # 如果置信度低于阈值且AI分类器可用，则使用AI
        if rule_result.confidence < 0.7 and self.ai_classifier:
            logger.info(f"规则分类置信度低({rule_result.confidence:.2f})，使用AI分类")
            return self.ai_classifier.classify(subject, body, from_addr)

        return rule_result

# 使用示例
if __name__ == "__main__":
    # 测试规则分类器
    classifier = RuleBasedClassifier()

    test_cases = [
        ("紧急：项目 deadline 今天", "项目需要在今天完成，请立即处理。", "boss@company.com"),
        ("每周新闻简报", "这是我们的每周新闻...", "newsletter@example.com"),
        ("自动回复：我在休假", "我正在休假，回来后会回复您。", "colleague@company.com"),
        ("普通邮件", "你好，最近怎么样？", "friend@example.com")
    ]

    for subject, body, from_addr in test_cases:
        result = classifier.classify(subject, body, from_addr)
        print(f"主题: {subject}")
        print(f"分类: {result.category.value} (置信度: {result.confidence:.2f})")
        print(f"建议操作: {result.suggested_actions}")
        print("-" * 50)