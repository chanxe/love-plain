# Love Plane ✈️

> 一个专为情侣打造的轻量级纪念日与日常记录应用，让爱意触手可及。

Love Plane 是一个基于 Flask 开发的单体 Web 应用，旨在提供一个简单、私密的空间来记录生活中的重要时刻。它无需复杂的部署，开箱即用，适合情侣之间共享美好回忆。

## ✨ 功能特性

### 核心功能

- **📅 纪念日记录 (Anniversary)**
  - 记录重要的日子，自动计算距离今天的天数
  - 支持多个纪念日管理
  - 智能排序，优先显示即将到来的纪念日

- **📝 日常动态 (Moments)**
  - 像朋友圈一样记录图文日常
  - 支持多图片上传
  - 点赞、评论互动功能
  - 支持按用户筛选和关键词搜索
  - 分页加载，性能优化

- **💬 亲密聊天 (Chat)**
  - 基于 WebSocket 的实时聊天功能
  - 支持文字消息实时收发
  - 私密安全的双人聊天空间

- **💕 爱的一天 (Love One Day)**
  - AI 智能生成每日播报
  - 支持语音播报功能
  - 回顾历史动态和纪念日
  - 自动缓存，提升性能

### 技术特性

- **📱 响应式设计**: 使用 Bootstrap 5，完美适配桌面和移动端
- **🔒 用户认证**: 基于 Token 的用户身份验证系统
- **🎨 现代化 UI**: 简洁优雅的界面设计
- **⚡ 高性能**: 数据库索引优化，查询效率高
- **🛡️ 安全**: 环境变量配置，敏感信息保护

## 🛠️ 技术栈

### 后端技术

- **编程语言**: Python 3.8+
- **Web 框架**: Flask
- **数据库**: SQLite (无需额外安装)
- **ORM**: SQLAlchemy
- **实时通信**: Flask-SocketIO
- **AI 服务**: 阿里云百炼 API (Qwen 模型)
- **语音合成**: Edge-TTS

### 前端技术

- **UI 框架**: Bootstrap 5
- **模板引擎**: Jinja2
- **实时通信**: Socket.IO Client
- **JavaScript**: 原生 ES6+

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 [Python 3.8+](https://www.python.org/)。

### 2. 获取代码

```bash
git clone https://github.com/chanxe/love-plain.git
cd love-plain
```

### 3. 安装依赖

建议使用虚拟环境：

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

安装项目依赖：

```bash
pip install -r requirements.txt
```

### 4. 配置环境

复制配置文件模板：

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# macOS/Linux
cp .env.example .env
```

编辑 `.env` 文件，配置以下环境变量：

```env
SECRET_KEY=your_secret_key_here
DATABASE_URI=sqlite:///love_plane.db

# AI 服务配置（可选）
BAILIAN_API_KEY=your_api_key_here
BAILIAN_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
BAILIAN_MODEL=qwen-max
BAILIAN_TEMPERATURE=0.8
BAILIAN_MAX_TOKENS=150
```

### 5. 初始化数据库

项目首次运行前，可以运行种子脚本来初始化测试数据（可选）：

```bash
python seed_data.py
```

注意：应用启动时也会自动创建数据库表结构。

### 6. 启动应用

```bash
python app.py
```

启动成功后，访问浏览器：`http://127.0.0.1:5000`

### 7. 用户登录

使用以下 Token 登录系统：

- **男性角色**: Token `ck`
- **女性角色**: Token `wkl`

## 📂 项目结构

```
love-plane/
├── app.py                    # 应用入口与主逻辑
├── ai_service.py             # AI 服务，包含播报生成逻辑
├── seed_data.py              # 数据库初始化脚本
├── clear_cache.py            # 清除缓存工具
├── requirements.txt          # 项目依赖
├── .env.example              # 环境变量模板
├── .gitignore                # Git 忽略规则
├── README.md                 # 项目说明文档
├── DEVELOPMENT_DOC.md        # 详细开发文档
├── CHAT_API.md               # 聊天功能 API 文档
├── MOMENTS_API.md            # 日常动态 API 文档
├── templates/                # HTML 模板
│   ├── base.html            # 基础布局
│   ├── index.html           # 首页
│   ├── login.html           # 登录页面
│   ├── moments.html         # 日常动态页面
│   ├── chat.html            # 聊天页面
│   └── anniversaries.html   # 纪念日管理页面
└── static/                   # 静态资源
    ├── uploads/             # 用户上传的图片
    └── reports/             # AI 生成的语音播报
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `SECRET_KEY` | Flask 密钥 | `default_dev_key` | 否 |
| `DATABASE_URI` | 数据库连接字符串 | `sqlite:///love_plane.db` | 否 |
| `BAILIAN_API_KEY` | 阿里云百炼 API 密钥 | - | 否 |
| `BAILIAN_ENDPOINT` | API 端点 | - | 否 |
| `BAILIAN_MODEL` | AI 模型名称 | - | 否 |
| `BAILIAN_TEMPERATURE` | 温度参数 | 0.8 | 否 |
| `BAILIAN_MAX_TOKENS` | 最大 Token 数 | 150 | 否 |

### 数据库配置

项目默认使用 SQLite 数据库，无需额外配置。如需使用其他数据库（如 MySQL、PostgreSQL），请修改 `.env` 文件中的 `DATABASE_URI`。

示例：

```env
# MySQL
DATABASE_URI=mysql+pymysql://user:password@localhost/love_plane

# PostgreSQL
DATABASE_URI=postgresql://user:password@localhost/love_plane
```

## 📖 使用指南

### 纪念日管理

1. 访问首页查看最近的纪念日
2. 点击"管理纪念日"进入纪念日管理页面
3. 添加新的纪念日，输入标题和日期
4. 系统自动计算距离今天的天数

### 发布日常动态

1. 点击导航栏的"日常动态"
2. 点击"发布动态"按钮
3. 输入内容，选择图片（可选）
4. 点击发布，动态将显示在列表中

### 实时聊天

1. 点击导航栏的"聊天室"
2. 输入消息内容
3. 按回车或点击发送按钮
4. 消息实时同步给对方

### 爱的一天播报

1. 访问首页，自动加载今日播报
2. 点击"播放语音"按钮收听播报
3. 点击"刷新"按钮重新生成播报
4. 点击"查看日常"跳转到日常动态页面

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境设置

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码风格
- 使用有意义的变量和函数名
- 添加必要的注释和文档字符串
- 确保代码通过测试

### 开发文档

详见 [DEVELOPMENT_DOC.md](DEVELOPMENT_DOC.md) 了解更多架构设计与开发细节。

## 📄 API 文档

- [日常动态 API](MOMENTS_API.md)
- [聊天功能 API](CHAT_API.md)

## 🐛 问题反馈

如果您遇到任何问题或有改进建议，请：

1. 查看现有的 [Issues](https://github.com/chanxe/love-plain/issues)
2. 创建新的 Issue，详细描述问题
3. 提供复现步骤和环境信息

## 📝 更新日志

### v1.0.0 (2026-01-17)

- ✨ 初始版本发布
- 📅 纪念日记录功能
- 📝 日常动态功能
- 💬 实时聊天功能
- 💕 爱的一天 AI 播报功能
- 🔒 用户认证系统

## � 安全说明

- 所有敏感信息都存储在环境变量中
- 用户 Token 认证确保访问安全
- 文件上传经过安全验证
- 数据库操作使用 ORM 防止 SQL 注入

## �📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 👨‍💻 作者

[chanxe](https://github.com/chanxe)

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Edge-TTS](https://github.com/rany2/edge-tts)

---

**让爱意触手可及，让回忆永存心间 ❤️**
