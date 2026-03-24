# AI电商客服实战模板部署指南

## 项目概述

本模板提供了一套完整的AI电商客服解决方案，包含：

1. **Dify工作流**：智能对话流程配置
2. **Coze Skill**：客服话术优化代码
3. **一键部署脚本**：Docker Compose全栈环境
4. **电商知识库**：产品、促销、话术模板

## 系统要求

- **操作系统**：Linux/Windows/macOS（推荐Linux）
- **Docker**：20.10+
- **Docker Compose**：2.0+
- **硬件**：
  - 最低：8GB RAM，20GB磁盘空间
  - 推荐：16GB RAM，50GB磁盘空间，GPU（可选）

## 快速开始

### 步骤1：下载项目文件

```bash
# 克隆GitHub仓库（或下载zip包）
git clone https://github.com/yourusername/ai-ecommerce-customer-service.git
cd ai-ecommerce-customer-service
```

### 步骤2：配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，设置以下变量
nano .env

# 必需配置：
SECRET_KEY=your-strong-secret-key-here
COZE_API_KEY=your-coze-api-key-optional
```

### 步骤3：下载AI模型（可选）

```bash
# 创建模型目录
mkdir -p models/qwen2.5-7b

# 从ModelScope下载Qwen2.5-7B模型（需提前安装modelscope）
# 或手动下载后放入目录
```

### 步骤4：启动所有服务

```bash
# 一键启动
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看日志
docker-compose logs -f dify-api
```

### 步骤5：访问控制台

- **Dify控制台**：http://localhost:3000
- **API文档**：http://localhost:5001
- **演示界面**：http://localhost:8080
- **向量数据库**：http://localhost:6333/dashboard

## 详细配置指南

### 1. Dify工作流导入

1. 登录Dify控制台 (http://localhost:3000)
2. 点击「创建工作流」
3. 选择「导入工作流」
4. 上传 `dify_ecommerce_customer_service_workflow.json`
5. 配置以下组件：
   - **知识库**：创建电商知识库，上传产品文档
   - **模型设置**：选择本地Qwen模型或OpenAI API
   - **发布应用**：生成可访问的API端点

### 2. Coze Skill部署

#### 方案A：部署到Coze平台
1. 登录Coze.cn
2. 创建新Skill
3. 复制 `coze_ecommerce_skill.js` 代码
4. 配置触发词和参数
5. 发布Skill

#### 方案B：本地运行
```bash
# 进入Coze Skill目录
cd coze-skill

# 安装依赖
npm install

# 启动服务
node coze_ecommerce_skill.js

# 测试API
curl -X POST http://localhost:3001/process \
  -H "Content-Type: application/json" \
  -d '{"message": "这件衣服适合什么场合？"}'
```

### 3. 电商知识库构建

#### 必需内容：
1. **产品信息**：规格、材质、价格、适用场景
2. **促销规则**：满减、优惠券、限时活动
3. **用户痛点**：尺码疑虑、物流时效、退换货政策
4. **转化话术**：应对"我再看看"、"太贵了"等场景

#### 格式建议：
- CSV文件：便于批量导入
- Markdown：结构化文档
- JSON：API对接

### 4. 集成到电商平台

#### 淘宝/天猫：
- 使用官方机器人接口
- 配置自动回复规则
- 设置关键词触发

#### 独立站：
- 网页嵌入Chat Widget
- API对接客服系统
- 微信小程序集成

#### 抖音/快手：
- 直播带货话术辅助
- 评论自动回复
- 私信客服机器人

## 实战案例：女装品牌部署记录

### 第一天：基础搭建（4小时）
1. 安装Docker和Docker Compose
2. 导入Dify工作流
3. 上传首批产品知识库（50个SKU）

### 第二天：对话优化（3小时）
1. 测试10个高频问题
2. 调整回答话术
3. 配置促销活动规则

### 第三天：小流量测试（2小时）
1. 10%咨询转AI客服
2. 收集用户反馈
3. 优化推荐逻辑

### 结果：
- **首周AI接待量**：87单
- **转化率**：AI 4.7% vs 人工 1.9%
- **客服加班时间减少**：62%

## 高级功能配置

### 1. 多轮对话设计
```json
{
  "场景": "价格疑虑",
  "步骤1": "确认用户关注点",
  "步骤2": "展示产品价值",
  "步骤3": "提供促销激励",
  "步骤4": "限时促单"
}
```

### 2. 个性化推荐
- 基于用户浏览历史
- 协同过滤算法
- 实时库存匹配

### 3. 数据监控看板
```bash
# 启动监控服务
docker-compose -f docker-compose.monitoring.yml up -d

# 访问Grafana
# http://localhost:3001
```

## 故障排除

### 常见问题1：Dify启动失败
```bash
# 检查端口冲突
netstat -tulpn | grep :3000

# 清理旧容器
docker-compose down -v
docker system prune -a

# 重新启动
docker-compose up -d
```

### 常见问题2：模型加载慢
```bash
# 使用CPU模式（降低内存要求）
# 修改docker-compose.yml中的qwen-api服务
environment:
  - DEVICE=cpu
  - MAX_LENGTH=2048
```

### 常见问题3：知识库检索不准
1. 优化文档分块策略（300-500字）
2. 添加元数据标签
3. 人工校准相似度阈值

## 性能优化建议

### 硬件层面：
- **CPU**：4核以上
- **内存**：16GB+（如需运行本地模型）
- **GPU**：RTX 3060+（加速推理）
- **存储**：SSD优先

### 软件层面：
- **模型量化**：使用4bit/8bit量化版本
- **缓存策略**：Redis缓存高频问答
- **CDN加速**：静态资源分发
- **负载均衡**：多实例部署

## 商务合作与定制

### 标准版包含：
- 完整源代码
- 部署指南
- 3个月基础支持
- 社群交流

### 高级版增加：
- 定制化开发
- 专人部署支持
- 数据迁移服务
- 长期维护更新

### 企业版专属：
- 私有化部署
- 二次开发培训
- SLA保障
- 源码授权

## 更新日志

### v1.0.0 (2026-03-24)
- 初始版本发布
- 包含基础工作流和技能
- 支持Dify和Coze双平台
- 提供一键部署脚本

---

## 获取支持

- **GitHub Issues**：技术问题反馈
- **微信社群**：扫码加入（见小鹅通课程页）
- **邮箱支持**：support@example.com
- **紧急联系**：+86 138-xxxx-xxxx

## 版权声明

本项目采用 MIT 许可证。商业使用请遵守相关协议。

---

**立即开始您的AI电商客服升级之旅！** 🚀

访问小鹅通课程页面获取完整教程：
[mrtuz.xet.tech/s/2kzI5t](https://mrtuz.xet.tech/s/2kzI5t)