# Love Plane ✈️

> 一个专为情侣/个人打造的轻量级纪念日与日常记录应用。

Love Plane 是一个基于 Flask 开发的单体 Web 应用，旨在提供一个简单、私密的空间来记录生活中的重要时刻。它无需复杂的部署，开箱即用。

## ✨ 功能特性

*   **📅 纪念日记录 (Anniversary)**: 记录重要的日子，自动计算距离今天的天数。
*   **📝 日常动态 (Moments)**: 像朋友圈一样记录图文日常（开发中）。
*   **💬 亲密聊天 (Chat)**: 基于 WebSocket 的实时聊天功能（开发中）。
*   **📱 响应式设计**: 使用 Bootstrap 5，适配桌面和移动端。

## 🛠️ 技术栈

*   **后端**: Python 3, Flask
*   **数据库**: SQLite (无需额外安装)
*   **实时通信**: Flask-SocketIO
*   **前端**: Bootstrap 5, Jinja2 模板

## 🚀 快速开始

### 1. 环境准备

确保您的系统已安装 [Python 3.8+](https://www.python.org/)。

### 2. 获取代码

```bash
git clone <repository-url>
cd love-plane
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

如果需要，可以编辑 `.env` 文件修改 `SECRET_KEY`。

### 5. 初始化数据库

项目首次运行前，可以运行种子脚本来初始化一些测试数据（可选）：

```bash
python seed_data.py
```
*(注意：应用启动时也会自动创建数据库表结构)*

### 6. 启动应用

```bash
python app.py
```

启动成功后，访问浏览器：`http://127.0.0.1:5000`

## 📂 项目结构

```
love-plane/
├── app.py              # 应用入口与主逻辑
├── seed_data.py        # 数据库初始化脚本
├── requirements.txt    # 项目依赖
├── .env                # 环境变量（不要提交到版本控制）
├── .gitignore          # Git 忽略规则
├── instance/           # 数据库文件存放目录
├── templates/          # HTML 模板
│   ├── base.html       # 基础布局
│   └── index.html      # 首页
└── DEVELOPMENT_DOC.md  # 详细开发文档
```

## 🤝 贡献与开发

详见 [DEVELOPMENT_DOC.md](DEVELOPMENT_DOC.md) 了解更多架构设计与开发细节。

## 📄 许可证

MIT License
