# 智能邮件处理系统

基于AI的邮件自动分类与处理系统，为企业提供高效的邮件管理解决方案。

## 功能特性

- **自动分类**: 使用规则和AI对邮件进行智能分类（紧急、重要、普通、垃圾邮件等）
- **优先级排序**: 根据分类自动标记优先级
- **自动处理**: 自动移动垃圾邮件、订阅邮件到指定文件夹
- **智能回复**: 可配置自动回复（开发中）
- **实时监控**: 定期检查新邮件并处理
- **详细日志**: 记录所有处理操作和结果

## 技术架构

```
┌─────────────────┐
│   IMAP服务器    │
│ (Gmail/Outlook) │
└────────┬────────┘
         │
┌────────▼────────┐
│  邮件处理器     │
│  ├─ 分类器      │
│  │  ├─ 规则分类 │
│  │  └─ AI分类   │
│  ├─ 动作执行器  │
│  └─ 结果记录器  │
└────────┬────────┘
         │
┌────────▼────────┐
│  处理结果       │
│  ├─ JSON日志    │
│  └─ 数据库      │
└─────────────────┘
```

## 快速开始

### 1. 环境设置

```bash
cd email_automation
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. 配置

复制环境变量模板并配置：

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的邮箱和API密钥
```

**Gmail配置说明**:
1. 启用Gmail的IMAP访问：[设置指南](https://support.google.com/mail/answer/7126229)
2. 生成应用专用密码：[生成指南](https://support.google.com/accounts/answer/185833)

### 3. 运行测试

```bash
# 测试分类器（无需真实邮箱）
python email_classifier.py

# 运行一次处理（需要配置邮箱）
python email_processor.py
```

### 4. 持续运行

```bash
# 修改 email_processor.py 中的 main() 函数
# 将 processor.run_once() 改为 processor.run_continuous()
# 然后运行
python email_processor.py
```

## 分类类别

| 类别 | 说明 | 默认操作 |
|------|------|----------|
| **urgent** | 紧急邮件，需要立即处理 | 标记红旗，保持原位 |
| **important** | 重要邮件，今天内处理 | 标记红旗，保持原位 |
| **normal** | 普通邮件，本周内处理 | 标记为已读 |
| **low** | 低优先级邮件 | 标记为已读 |
| **spam** | 垃圾邮件 | 移动到垃圾邮件文件夹 |
| **auto_reply** | 自动回复 | 移动到存档文件夹 |
| **newsletter** | 订阅邮件 | 移动到存档文件夹 |

## 配置说明

### 邮箱配置
- `EMAIL_IMAP_SERVER`: IMAP服务器地址（默认: imap.gmail.com）
- `EMAIL_IMAP_PORT`: IMAP端口（默认: 993）
- `EMAIL_ADDRESS`: 邮箱地址
- `EMAIL_PASSWORD`: 邮箱密码或应用专用密码
- `EMAIL_USE_SSL`: 是否使用SSL（默认: true）

### AI配置
- `OPENAI_API_KEY`: OpenAI API密钥（可选）
- `AI_CLASSIFICATION_ENABLED`: 是否启用AI分类（默认: false）
- `AI_MIN_CONFIDENCE_THRESHOLD`: AI分类置信度阈值（0-1）

### 处理配置
- `CHECK_INTERVAL_MINUTES`: 检查间隔（分钟）
- `MAX_EMAILS_PER_CHECK`: 每次检查最大邮件数
- `ARCHIVE_PROCESSED`: 是否自动存档处理过的邮件
- `ARCHIVE_FOLDER`: 存档文件夹名称
- `SPAM_FOLDER`: 垃圾邮件文件夹名称

## API使用示例

### 基本分类

```python
from email_classifier import RuleBasedClassifier

classifier = RuleBasedClassifier()
result = classifier.classify(
    subject="紧急：项目 deadline 今天",
    body="项目需要在今天完成，请立即处理。",
    from_addr="boss@company.com"
)

print(f"分类: {result.category.value}")
print(f"置信度: {result.confidence}")
print(f"建议操作: {result.suggested_actions}")
```

### 混合分类（规则+AI）

```python
from email_classifier import HybridClassifier

# 需要设置 OPENAI_API_KEY 环境变量
classifier = HybridClassifier(api_key="your-api-key")
result = classifier.classify(subject, body, from_addr)
```

### 邮件处理

```python
from email_processor import EmailProcessor
from config import load_config

config = load_config()
processor = EmailProcessor(config)

# 处理一次
results = processor.run_once()

# 持续处理
processor.run_continuous()
```

## 扩展开发

### 添加新分类规则

编辑 `email_classifier.py` 中的 `RuleBasedClassifier.rules` 字典：

```python
self.rules[EmailCategory.NEW_CATEGORY] = {
    'keywords': ['关键词1', '关键词2'],
    'subject_patterns': [r'正则表达式'],
    'from_patterns': [r'发件人模式']
}
```

### 添加新操作

在 `EmailProcessor._take_actions` 方法中添加对新分类的处理逻辑：

```python
elif classification.category == EmailCategory.NEW_CATEGORY:
    # 执行自定义操作
    self._custom_action(email_id)
```

### 集成SMTP自动回复

1. 在配置中启用自动回复：`AUTO_REPLY_ENABLED=true`
2. 实现 `_send_auto_reply` 方法，使用SMTP发送回复邮件

## 性能优化

1. **批量处理**: 一次处理多封邮件，减少API调用
2. **缓存机制**: 缓存常见发件人和主题的分类结果
3. **离线分类**: 对于高置信度规则分类，跳过AI分类
4. **并发处理**: 使用多线程处理大量邮件

## 成本控制

### AI分类成本估算

- GPT-3.5-turbo: $0.0015/1K tokens（输入+输出）
- 平均每封邮件: 100 tokens
- 每月10,000封邮件: 1M tokens = $1.5
- 每月100,000封邮件: 10M tokens = $15

### 建议优化

1. 仅对低置信度规则分类使用AI
2. 设置每天/每月AI分类上限
3. 使用更小的模型或本地模型

## 部署方案

### 方案一：本地运行（推荐用于测试）
- 在个人电脑或服务器上运行
- 使用系统定时任务（cron/Windows任务计划）
- 适合小型团队或个人使用

### 方案二：云服务器部署
- 部署到AWS EC2、Google Cloud、Azure等
- 使用Docker容器化
- 配置自动重启和监控

### 方案三：SaaS服务
- 多租户架构
- Web管理界面
- 按月订阅收费

## 安全注意事项

1. **密码安全**: 使用应用专用密码，不要使用主密码
2. **API密钥**: 妥善保管OpenAI API密钥，不要提交到版本控制
3. **数据加密**: 传输和存储邮件内容时考虑加密
4. **访问权限**: 限制对处理结果的访问权限

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查IMAP服务器和端口
   - 确认邮箱已启用IMAP访问
   - 验证密码是否正确

2. **AI分类失败**
   - 检查OpenAI API密钥是否有效
   - 确认网络连接
   - 查看API使用额度

3. **邮件处理缓慢**
   - 减少每次检查的邮件数量
   - 关闭AI分类或提高置信度阈值
   - 优化网络连接

### 日志查看

```bash
# 查看实时日志
tail -f email_automation.log

# 搜索错误
grep ERROR email_automation.log
```

## 商业应用

### 目标客户
- 中小型企业（10-500人）
- 客服团队
- 销售团队
- 高管个人助理

### 定价策略（参考）
- **基础版**: $299/月，支持1个邮箱，规则分类
- **专业版**: $799/月，支持5个邮箱，AI分类+自动回复
- **企业版**: $1499/月，支持20个邮箱，定制工作流+SLA

### 竞争优势
1. **高性价比**: API成本低，利润率90%+
2. **易集成**: 支持主流邮箱服务
3. **可扩展**: 模块化设计，易于定制
4. **自动化**: 7×24小时运行，减少人工干预

## 路线图

### v1.0（当前）
- [x] 基础规则分类
- [x] IMAP邮件处理
- [x] 基本邮件操作（标记、移动）
- [x] 日志记录

### v1.1（计划中）
- [ ] SMTP自动回复
- [ ] Web管理界面
- [ ] 多邮箱支持
- [ ] 高级统计报表

### v1.2（计划中）
- [ ] 机器学习模型训练
- [ ] 自定义分类规则
- [ ] API接口
- [ ] 移动端通知

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目为商业SaaS产品核心组件，核心代码受版权保护。

## 支持

如有问题或建议，请通过以下方式联系：
- 邮箱: chu25267@gmail.com
- GitHub Issues: [提交问题](https://github.com/your-repo/issues)

---

**立即开始**: 配置你的邮箱，体验智能邮件处理的便捷！