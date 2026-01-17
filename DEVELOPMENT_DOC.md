# Love Plane - 开发文档

## 1. 系统架构设计

### 1.1 架构模式
本项目采用 **单体架构 (Monolithic Architecture)** 结合 **MVC (Model-View-Controller)** 设计模式。
- **理由**: 项目定位为个人/情侣使用的轻量级应用，单体架构开发维护成本最低，部署简单，无需微服务带来的复杂性。

### 1.2 分层设计
系统逻辑上前主要分为三层：
- **表现层 (Presentation Layer)**:
    - 由 Flask 的 Jinja2 模板引擎渲染 HTML 页面。
    - 使用 Bootstrap 5 提供响应式 UI 组件。
    - 使用 JavaScript (Socket.IO client) 处理前端实时交互。
- **业务逻辑层 (Business Logic Layer)**:
    - `app.py` 中的视图函数 (Routes) 处理 HTTP 请求和业务流转。
    - WebSocket 事件处理函数负责即时通讯逻辑。
- **数据访问层 (Data Access Layer)**:
    - 使用 SQLAlchemy ORM 封装数据库操作。
    - `models` 定义数据结构，隔离 SQL 细节。

### 1.3 架构图
```mermaid
graph TD
    User[用户 (Browser)] <-->|HTTP/WebSocket| Flask[Flask Web Server]
    subgraph "Backend (Flask)"
        Route[路由/视图] --> Controller[业务逻辑]
        Controller --> ORM[SQLAlchemy ORM]
        Socket[Socket.IO Handler] --> Controller
    end
    ORM <-->|Read/Write| SQLite[(SQLite Database)]
```

---

## 2. 技术栈规划

### 2.1 前端技术栈
- **框架选择**: 
    - **Bootstrap 5**: 选型理由是其提供了丰富的预设组件（卡片、导航栏、按钮），无需编写复杂 CSS 即可实现现代化 UI。
    - **Jinja2**: Flask 内置模板引擎，适合服务端渲染 (SSR) 模式，简化了前后端数据传递。
- **UI组件库**: Bootstrap 5 Native Components。
- **状态管理**: 简单应用通过 DOM 直接操作，无需 Redux/Vuex 等复杂状态管理。
- **构建工具**: 无需 Webpack/Vite，直接引入 CDN 资源，保持开发环境极致轻量。

### 2.2 后端技术栈
- **编程语言**: **Python 3.x**。
    - **选型依据**: 用户熟悉 Python，且 Python 生态丰富，开发效率高。
- **Web框架**: **Flask**。
    - **选型依据**: 轻量级（Micro-framework），灵活性高，核心简单，插件丰富（如 Flask-SQLAlchemy, Flask-SocketIO）。
    - **备选方案**: Django（太重，配置复杂），FastAPI（适合纯 API 开发，本项目含页面渲染，Flask 更顺手）。
- **数据库**: **SQLite**。
    - **选型依据**: 单文件数据库，零配置，无需安装额外服务，完美适配个人项目。
    - **备选方案**: MySQL/PostgreSQL（需要额外部署，对于单用户/双用户场景属于过度设计）。
- **即时通讯**: **Flask-SocketIO**。
    - **选型依据**: 封装了 WebSocket 协议，提供房间机制，自动处理连接降级（Polling）。

### 2.3 基础设施
- **容器化**: 暂不需要，直接本地运行 `python app.py`。
- **CI/CD**: 手动部署或 Git 同步。
- **监控**: Flask 内置 Debug 模式。

---

## 3. 功能模块分解

### 3.1 纪念日模块 (Anniversary)
- **功能说明**: 记录和展示恋爱中的重要日期，计算天数。
- **输入**: 标题 (String), 日期 (Date)。
- **输出**: 纪念日列表，距离今天的天数。
- **业务流程**: 用户输入 -> 存入数据库 -> 首页按时间排序展示。

### 3.2 日常动态模块 (Moments)
- **功能说明**: 类似朋友圈/日记，记录图文日常。
- **输入**: 内容 (Text), 图片 (Optional), 时间 (Automatic)。
- **输出**: 时间轴形式展示的动态流。

### 3.3 亲密聊天模块 (Chat)
- **功能说明**: 实时文字通讯。
- **输入**: 消息内容。
- **输出**: 实时推送到对方屏幕。
- **技术实现**: WebSocket 全双工通信。

### 3.4 爱的一天模块 (Love One Day)
- **功能说明**: AI 智能生成每日播报，回顾历史动态和纪念日。
- **输入**: 历史动态数据、纪念日数据、当前日期。
- **输出**: 每日播报文本、语音播报文件。
- **技术实现**: 
  - 使用阿里云百炼 API (Qwen 模型) 生成播报内容
  - 使用 Edge-TTS 生成语音播报
  - 数据库缓存每日播报，避免重复生成

---

## 4. 接口规范

本项目主要采用 **服务端渲染 (SSR)**，大部分交互通过页面跳转完成，少部分通过 AJAX/WebSocket。

### 4.1 路由设计 (Routes)
- `GET /`: 首页，加载纪念日数据。
- `GET /moments`: 动态列表页。
- `POST /moments/add`: 发布新动态。
- `GET /chat`: 聊天页面。

### 4.2 WebSocket 事件 (Socket.IO)
- **Event**: `message`
    - **Direction**: Client -> Server
    - **Payload**: `{'data': '消息内容'}`
- **Event**: `response`
    - **Direction**: Server -> Client
    - **Payload**: `{'data': '消息内容', 'time': 'timestamp'}`

---

## 5. 核心业务流程

### 5.1 发布动态流程
1. 用户在 `/moments` 页面点击“发布”。
2. 填写表单（内容）。
3. 点击提交 -> `POST /moments/add`。
4. 后端验证数据 -> 写入 `moment` 表。
5. 后端重定向回 `/moments` -> 页面重新渲染显示新动态。

### 5.2 实时聊天流程
1. 用户 A 打开 `/chat` -> 建立 WebSocket 连接。
2. 用户 A 输入消息并发送 -> 触发前端 `socket.emit('message')`。
3. 后端接收事件 -> 存储消息（可选） -> 广播 `emit('response', broadcast=True)`。
4. 用户 B (在线) 收到 `response` 事件 -> JavaScript 将消息追加到聊天窗口 DOM。

---

## 6. 纪念日分页功能专项说明

### 6.1 业务逻辑
- **触发条件**: 当系统内纪念日总数超过 5 个时，首页卡片仅显示最近 5 个，并显示“查看全部”按钮。
- **展示模式**: 点击按钮后，弹出模态框 (Modal) 显示完整列表。
- **分页逻辑**: 
    - 采用 **前端分页**，一次性获取所有数据，减少服务器请求。
    - 每页显示 5-8 条（默认 5 条）。
    - 提供“上一页”、“下一页”及页码显示。

### 6.2 交互设计
- **响应式**: 适配移动端和桌面端。
- **动画**: 列表切换时支持平滑过渡效果。
- **手势**: 移动端支持左右滑动切换页码。
- **键盘**: 桌面端支持左右方向键切换页码。
- **加载状态**: 数据加载过程中显示 Loading 提示。

### 6.3 技术实现
- **接口**: 调整 `/api/anniversaries`，支持获取全部数据（如 `per_page=-1`）。
- **前端**: 
    - 使用 JavaScript 维护 `allAnniversaries` 数组。
    - `renderPage(pageIndex)` 函数负责计算切片并渲染 DOM。
    - 监听 `touchstart/touchend` 实现滑动。
    - 监听 `keydown` 实现键盘导航。

### 6.4 测试用例
1. **基础功能**: 
   - 数据 < 5 时，不显示“查看全部”。
   - 数据 > 5 时，显示按钮，点击弹出 Modal。
2. **分页验证**: 
   - 首页显示正确（第1页）。
   - 翻页功能正常（上下页）。
   - 边界处理（第一页按上一页无效，最后一页按下一页无效）。
3. **交互验证**: 
   - 手机模式下左滑翻下一页，右滑翻上一页。
   - 键盘左右键可翻页。

---

## 7. 日常动态模块详解 (Moments Specs)

### 7.1 功能概述
日常动态模块旨在记录情侣间的点滴生活，支持图文发布、查看、互动。
- **动态展示**: 支持图文混排，每条动态显示发布时间、发布者信息、互动数据（点赞/评论数）。
- **分页加载**: 采用瀑布流/列表形式，默认每页 20 条。支持下拉刷新（获取最新数据）和上滑加载更多（获取历史数据）。
- **多维查询**: 支持按时间范围（最近7天/1个月/自定义）、发布者、内容关键词进行筛选，支持组合查询及模糊/精确模式切换。

### 7.2 接口定义 (API Definitions)

#### 7.2.1 获取动态列表
- **URL**: `GET /api/moments`
- **Description**: 根据条件筛选并分页返回动态列表。

### 7.3 参数说明 (Query Parameters)

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `page` | Integer | 否 | 1 | 当前页码 |
| `per_page` | Integer | 否 | 20 | 每页显示条数 |
| `start_date` | Date | 否 | - | 筛选起始日期 (YYYY-MM-DD) |
| `end_date` | Date | 否 | - | 筛选结束日期 (YYYY-MM-DD) |
| `user_id` | Integer | 否 | - | 发布者 ID |
| `keyword` | String | 否 | - | 搜索关键词 |
| `mode` | String | 否 | `fuzzy` | 搜索模式: `fuzzy` (模糊), `exact` (精确) |

### 7.4 响应示例 (Response Example)

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 101,
        "content": "今天和宝宝去看了电影，开心！",
        "images": ["/static/uploads/img_01.jpg"],
        "publisher": {
          "id": 1,
          "name": "Boy",
          "avatar": "/static/avatars/boy.png"
        },
        "created_at": "2023-10-01 14:30:00",
        "stats": {
          "likes": 12,
          "comments": 3
        }
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 98,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 7.5 异常处理与错误代码

#### 异常处理策略
1.  **网络中断**: 前端捕获网络错误，显示“网络连接已断开”提示，并提供重试按钮。
2.  **查询超时**: 后端设置 10 秒超时阈值。若超时，返回 HTTP 504，前端提示“请求超时，请优化查询条件”。
3.  **分页越界**: 当请求 `page` 大于 `total_pages` 时，返回空列表 (`items: []`)，不抛出错误。

#### 错误代码表

| HTTP Code | Error Code | 说明 | 解决方案 |
| :--- | :--- | :--- | :--- |
| 400 | `INVALID_PARAM` | 参数格式错误 (如日期格式不对) | 检查输入参数格式 |
| 504 | `QUERY_TIMEOUT` | 查询超时 (超过 10s) | 缩小查询的时间范围或关键词 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 | 联系开发人员检查日志 |

### 7.6 性能指标要求
- **索引优化**: 数据库需对 `created_at`, `user_id` 及 `content` (如支持全文检索) 字段建立索引。
- **响应速度**: 普通分页查询 < 200ms；复杂组合查询 < 500ms。
- **前端性能**: 列表页首屏渲染时间 (FCP) < 1s；加载更多时的渲染延迟 < 300ms。

---

## 8. 亲密聊天模块详解 (Chat Specs)

### 8.1 功能概述
提供情侣间专属的私密实时通讯空间，强调即时性与互动感。
- **实时消息**: 基于 WebSocket 的低延迟文字传输。
- **历史记录**: 消息持久化存储，支持进入聊天室自动加载最近消息，向上滚动加载更多历史。
- **状态感知**: 
    - **在线状态**: 实时显示对方是否在线。
    - **输入状态**: 对方正在输入时，顶部标题栏显示 "对方正在输入..."。
- **体验优化**: 
    - 消息发送失败重试提示。
    - 收到新消息自动滚动到底部。
    - 自己的消息显示在右侧，对方的消息显示在左侧。

### 8.2 交互流程设计

1.  **连接阶段**:
    - 用户进入 `/chat` 页面。
    - 前端初始化 Socket.IO 客户端，建立连接。
    - 调用 `GET /api/chat/history` 加载最近 20 条消息。
    - 界面显示 "连接成功"，若对方在线，头像旁显示绿点。

2.  **消息发送**:
    - 用户输入文字，点击发送。
    - 前端立即将消息渲染到右侧（半透明状态），并清除输入框。
    - 发送 `message` 事件给服务端。
    - 服务端确认接收并广播后，前端将消息置为正常状态（不透明）。

3.  **消息接收**:
    - 监听 `response` 事件。
    - 判断消息发送者：
        - 若是自己（多端同步），渲染在右侧。
        - 若是对方，渲染在左侧。
    - 若当前视图在底部，自动滚动显示新消息；若在查看历史，显示 "新消息提醒" 气泡。

4.  **输入状态**:
    - 监听输入框 `input` 事件，防抖发送 `typing` 事件。
    - 监听 `blur` 或发送消息后，发送 `stop_typing` 事件。

### 8.3 接口与协议定义

#### 8.3.1 HTTP 接口 (REST)
- **获取历史消息**
    - **URL**: `GET /api/chat/history`
    - **Query**: 
        - `before_id` (Int, Optional): 消息 ID 游标，用于分页。
        - `limit` (Int): 默认 20。
    - **Response**:
        ```json
        {
            "items": [
                {"id": 100, "sender_id": 1, "content": "Hello", "timestamp": "2023-10-27 10:00:00"}
            ],
            "has_more": true
        }
        ```

#### 8.3.2 WebSocket 事件 (Socket.IO)
| 事件名 | 方向 | Payload 示例 | 说明 |
| :--- | :--- | :--- | :--- |
| `join` | C -> S | `{ "room": "couple_1" }` | 加入房间 |
| `message` | C -> S | `{ "content": "I love you" }` | 发送消息 |
| `response` | S -> C | `{ "id": 101, "sender_id": 1, "content": "...", "time": "..." }` | 接收消息广播 |
| `typing` | C -> S | `{}` | 开始输入 |
| `stop_typing` | C -> S | `{}` | 停止输入 |
| `status_change`| S -> C | `{ "user_id": 2, "status": "typing/online/offline" }` | 状态变更通知 |

### 8.4 异常处理
- **连接断开**: 
    - 界面顶部显示红色横条 "连接断开，正在重连..."。
    - Socket.IO 客户端开启自动重连 (Reconnection)。
- **发送失败**: 
    - 超过 5秒 未收到服务端确认。
    - 消息气泡旁显示红色感叹号，点击可重试。

---

## 10. 爱的一天模块详解 (Love One Day Specs)

### 10.1 功能概述
爱的一天模块是系统的核心功能之一，通过 AI 智能分析历史数据和纪念日，生成个性化的每日播报，帮助情侣回顾美好时光。

- **智能播报生成**: 基于历史动态、纪念日等数据，AI 生成温馨的每日播报内容
- **语音播报**: 支持将播报文本转换为语音，提供更好的听觉体验
- **历史回顾**: 自动识别历史上的今天（往年同一天）的重要事件和动态
- **缓存机制**: 每日播报缓存到数据库，避免重复生成，提升性能
- **定时推送**: 支持定时任务自动生成播报并推送给用户

### 10.2 业务流程

#### 10.2.1 播报生成流程
1. **数据收集**: 收集今日的纪念日、历史动态、历史趣事等数据
2. **AI 生成**: 调用阿里云百炼 API，根据收集的数据生成播报内容
3. **内容限制**: 严格控制生成内容在 100 字以内，确保界面显示效果
4. **语音合成**: 使用 Edge-TTS 将播报文本转换为语音文件
5. **数据存储**: 将播报内容和语音文件路径保存到数据库
6. **前端展示**: 首页自动加载今日播报，用户可查看或播放语音

#### 10.2.2 播报类型
- **纪念日播报**: 今天是某个重要纪念日，生成祝福和回顾
- **历史日常播报**: 历史上今天有超过 3 条动态，生成怀旧回顾
- **历史趣事播报**: 历史上今天有有趣的动态，生成趣味回顾
- **综合播报**: 结合多种数据类型，生成综合性播报

### 10.3 数据库模型

#### LoveOneDayReport 表
```python
class LoveOneDayReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_date = db.Column(db.Date, unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    broadcast_type = db.Column(db.String(50), nullable=False)
    audio_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_pushed = db.Column(db.Boolean, default=False)
```

**字段说明**:
- `report_date`: 播报日期，设置唯一索引确保每天只有一条播报
- `content`: 播报内容文本，最多 100 字
- `broadcast_type`: 播报类型（anniversary/historical_events/historical_moments）
- `audio_url`: 语音文件路径
- `is_pushed`: 是否已通过定时任务推送

### 10.4 接口定义 (API Definitions)

#### 10.4.1 获取今日播报
- **URL**: `GET /api/love-one-day/today`
- **Description**: 获取今日播报内容，优先从缓存读取
- **Response**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "text": "今天是我们的纪念日，回想起来真是美好...",
    "date": "2026年01月17日",
    "broadcast_type": "anniversary",
    "audio_url": "/static/reports/love_one_day_report_20260117.mp3",
    "created_at": "2026-01-17 06:00:00"
  }
}
```

#### 10.4.2 生成语音播报
- **URL**: `POST /api/love-one-day/tts`
- **Description**: 将播报文本转换为语音文件
- **Request Body**:
```json
{
  "text": "播报内容文本",
  "report_id": 1
}
```
- **Response**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "audio_url": "/static/reports/love_one_day_report_20260117.mp3"
  }
}
```

#### 10.4.3 获取历史播报列表
- **URL**: `GET /api/love-one-day/history`
- **Description**: 获取历史播报列表，支持分页
- **Query Parameters**:
  - `page`: 页码（默认 1）
  - `per_page`: 每页数量（默认 10）
- **Response**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "text": "播报内容...",
        "date": "2026年01月17日",
        "broadcast_type": "anniversary",
        "audio_url": "/static/reports/xxx.mp3"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_items": 100,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### 10.5 AI 服务配置

#### 10.5.1 环境变量
```env
BAILIAN_API_KEY=sk-bacb58fe4db14cef836c2767adbfad46
BAILIAN_ENDPOINT=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
BAILIAN_MODEL=qwen-max
BAILIAN_TEMPERATURE=0.8
BAILIAN_MAX_TOKENS=150
```

#### 10.5.2 Prompt 设计
- **纪念日模式**: 简化 prompt，直接要求生成 100 字以内的播报
- **历史日常模式**: 简化 prompt，聚焦怀旧情感
- **历史趣事模式**: 简化 prompt，突出趣味性

#### 10.5.3 内容长度控制
```python
# 在 API 调用中设置 max_tokens 参数
payload = {
    "max_tokens": 150,  # 限制 token 数量
}

# 在返回结果中截断内容
content = result['choices'][0]['message']['content'].strip()
return content[:100] if len(content) > 100 else content
```

### 10.6 性能优化

#### 10.6.1 数据库索引
```python
# LoveOneDayReport 表
__table_args__ = (
    db.Index('idx_report_date', 'report_date'),
)
```

#### 10.6.2 缓存策略
- **数据库缓存**: 每日播报存储在数据库，避免重复生成
- **前端缓存**: 播报内容在页面加载时获取，避免频繁请求
- **音频缓存**: 生成的音频文件保存在服务器，可重复播放

### 10.7 定时任务
```python
def schedule_daily_broadcast():
    def broadcast_worker():
        while True:
            now = datetime.now()
            today = date.today()
            
            if now.hour == 6 and now.minute == 0:
                with app.app_context():
                    existing_report = LoveOneDayReport.query.filter_by(report_date=today).first()
                    
                    if not existing_report:
                        # 生成今日播报
                        data = LoveOneDayService.collect_daily_data()
                        report_text = LoveOneDayService.generate_love_broadcast(data)
                        
                        # 保存到数据库
                        new_report = LoveOneDayReport(
                            report_date=today,
                            content=report_text,
                            broadcast_type=broadcast_type,
                            is_pushed=True
                        )
                        db.session.add(new_report)
                        db.session.commit()
                        
                        # WebSocket 推送
                        socketio.emit('love_one_day_broadcast', {...}, room='couple_room')
            
            time.sleep(60)
```

### 10.8 异常处理
- **API 调用失败**: 捕获异常，返回友好的错误提示
- **语音生成失败**: 提供重试机制，或使用默认语音
- **数据库错误**: 记录日志，返回空数据
- **网络超时**: 设置合理的超时时间，避免长时间等待

---

## 11. 文档维护机制

- **版本控制**: 文档随代码仓库 (`Git`) 一同管理，位于项目根目录。
- **同步机制**: 每次架构调整或新增模块时，需在 Pull Request 中更新本文档。
- **更新频率**: 每次重大功能更新后，及时更新相关章节。
