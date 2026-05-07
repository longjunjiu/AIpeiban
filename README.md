# AIpeiban - AI陪伴系统

<div align="center">

[![Stars](https://img.shields.io/github/stars/longjunjiu/AIpeiban?style=social)](https://github.com/longjunjiu/AIpeiban/stargazers)
[![Fork](https://img.shields.io/github/forks/longjunjiu/AIpeiban?style=social)](https://github.com/longjunjiu/AIpeiban/network/members)
[![License](https://img.shields.io/github/license/longjunjiu/AIpeiban)](https://github.com/longjunjiu/AIpeiban/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**用AI复制不在身边或已经离去的人，让爱与记忆永不消逝**

[项目文档](./docs/feasibility-report.md) · [快速开始](#快速开始) · [路线图](#roadmap) · [参与贡献](#参与贡献) · [许可证](#许可证)

</div>

---

## 📖 项目简介

AIpeiban（AI陪伴）是一个开源的AI陪伴系统，旨在帮助用户保存和延续与重要人物之间的情感连接。通过分析用户提供的文字、语音等素材，我们的系统能够学习特定人物的性格特征、说话方式和表达习惯，然后以这个人物的"身份"与用户进行自然、富有情感的对话交流。

### 核心价值

**情感延续**：当亲人不在身边或已经离去时，AI陪伴系统可以成为连接过去与现在的桥梁，帮助保存珍贵的情感记忆。

**隐私优先**：支持完全本地部署，所有数据存储在本地，确保用户隐私安全。

**开源透明**：代码完全开源，算法透明可见，用户可以完全控制自己的数据和系统。

## ✨ 核心功能

### 🤖 智能对话
- 基于大语言模型的自然语言对话
- 支持多轮上下文记忆，保持对话连贯性
- 情感感知与回应，让对话更有温度

### 👤 人格档案
- 创建专属的人格档案，记录重要人物的性格特征
- 支持导入多种数据格式（文字、语音等）
- 人格相似度评估，持续优化复现效果

### 🔬 模型蒸馏
- 支持LoRA、QLoRA、Prompt Tuning等多种蒸馏方法
- 可集成女娲(Nvwa)技能进行高效蒸馏
- 将大模型知识蒸馏到轻量级个性化模型
- 支持模型量化和剪枝优化

### 🔒 隐私保护
- 本地优先存储，数据不上传云端
- 人格档案加密保护
- 清晰的隐私政策，用户完全掌控数据

### 🛠️ 灵活部署
- 支持本地部署（Ollama、llama.cpp）
- 支持云端API调用（OpenAI、Claude等）
- Docker一键部署，开箱即用

## 🚀 快速开始

### 环境要求

- Python 3.10 或更高版本
- 至少 8GB 内存（本地模型建议 16GB）
- 可选：NVIDIA 显卡（用于加速本地模型推理）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/longjunjiu/AIpeiban.git
cd AIpeiban
```

#### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 配置模型

**方案A：使用本地模型（推荐）**

安装并启动 Ollama：

```bash
# 安装 Ollama（macOS/Linux）
curl -fsSL https://ollama.com/install.sh | sh

# 启动 Ollama 服务
ollama serve

# 下载模型（以 Qwen 为例）
ollama pull qwen2.5
```

**方案B：使用云端API**

编辑 `config.yaml` 配置文件，填入你的 API Key：

```yaml
llm:
  provider: "openai"  # 或 "claude", "zhipu"
  api_key: "your-api-key-here"
  model: "gpt-4"
```

#### 5. 启动应用

```bash
python main.py
```

访问 http://localhost:7860 开始使用！

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Web 界面   │  │  命令行工具  │  │     API 接口        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Skill层                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              AI陪伴Skill                            │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │    │
│  │  │人格档案  │  │对话引擎  │  │   模型蒸馏器     │  │    │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                        模型层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  大模型    │→ │ 蒸馏器     │→ │  个性化小模型      │  │
│  │  (Ollama)  │  │ (Nvwa)     │  │  (LoRA/QLoRA)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                        数据层                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  SQLite     │  │   Redis     │  │    本地文件系统      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 核心技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 后端框架 | FastAPI | 高性能异步Web框架 |
| 语言模型 | Ollama / OpenAI API | 灵活的模型调用 |
| 模型蒸馏 | PEFT (LoRA/QLoRA) | 参数高效微调 |
| 数据存储 | SQLite + Redis | 轻量级本地存储 |
| 前端界面 | Gradio | 快速构建AI应用界面 |
| 对话管理 | LangChain | 链式对话组件 |
| 语音处理 | Whisper + Edge-TTS | 语音识别与合成 |

### Skill架构

AI陪伴系统以Skill形式提供，便于集成到各种AI助手平台：

```python
# 使用AI陪伴Skill
from ai_companion import AICompanion

# 创建实例
companion = AICompanion()

# 创建人格档案
companion.create_persona(
    name="奶奶",
    description="温柔善良的老奶奶"
)

# 蒸馏个性化模型（支持女娲集成）
companion.distill_model("奶奶", method="lora")

# 开始对话
response = companion.chat("奶奶", "奶奶，我想你了")
```

## 📋 Roadmap

```
📌 v0.1.0 - MVP（当前阶段）
├── ✅ 基础对话功能
├── ✅ 简单的人格档案管理
├── ✅ AI陪伴Skill框架
├── ✅ 模型蒸馏模块（LoRA/QLoRA）
├── 🔄 Web聊天界面
└── 📝 基础配置管理

📌 v0.2.0 - 语音交互
├── 🔲 语音识别集成
├── 🔲 语音合成功能
├── 🔲 语音对话界面
└── 🔲 多语言支持

📌 v0.3.0 - 女娲集成
├── 🔲 女娲Skill蒸馏API集成
├── 🔲 分布式蒸馏任务管理
├── 🔲 模型量化优化
└── 🔲 蒸馏模型仓库

📌 v1.0.0 - 人格深度定制
├── 🔲 多源数据人格特征提取
├── 🔲 人格向量可视化
├── 🔲 自适应学习机制
└── 🔲 个性化调优工具

📌 v2.0.0 - 生态建设
├── 🔲 人格档案分享市场
├── 🔲 第三方插件系统
├── 🔲 社区交流平台
└── 🔲 更多集成选项
```

## 💡 使用场景

### 家庭记忆传承
保存祖父母、父母等长辈的人生故事和智慧，让后代能够跨越时空与他们"对话"。

### 远距离情感连接
为因工作、学习等原因分隔两地的家人提供一种新的情感交流方式。

### 心理慰藉支持
为失去亲人的人们提供一个安全的空间，在悲伤处理过程中获得情感支持。

### 个人数字遗产
创建自己的AI版本，将个人经历、价值观和智慧留给后代。

## ⚠️ 伦理声明

使用本项目时，请遵守以下原则：

1. **知情同意**：创建他人的人格档案前，请获得本人或其直系亲属的明确同意
2. **真实告知**：明确认识到对话对象是AI，而非真实的人
3. **健康使用**：将AI陪伴作为情感支持的一部分，而非替代真实的人际交往
4. **隐私保护**：妥善保管相关数据和材料

我们建议用户在需要心理健康支持时，寻求专业的心理咨询服务。

## 🤝 参与贡献

欢迎各种形式的贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 如何参与

- 🐛 报告 Bug 或提交 Issue
- 💡 提出新功能建议
- 📝 完善文档
- 🔧 提交 Pull Request
- 🌐 翻译文档到其他语言

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 开源，欢迎在使用后进行传播和修改。

## 📬 联系方式

- GitHub Issues: [提交问题](https://github.com/longjunjiu/AIpeiban/issues)
- 讨论区: [GitHub Discussions](https://github.com/longjunjiu/AIpeiban/discussions)

---

**让爱与记忆永不消逝** | 让思念有处安放
