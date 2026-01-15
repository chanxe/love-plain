# Love Plane - 亲密聊天模块 API 文档

本文档描述了亲密聊天模块 (Chat) 的后端接口及 WebSocket 事件定义。

## 1. 数据模型

### Message (消息)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | Integer | 主键 |
| sender_id | Integer | 发送者 ID (外键关联 User) |
| content | Text | 消息内容 |
| timestamp | DateTime | 发送时间 |

---

## 2. HTTP 接口

### 2.1 获取历史消息
- **URL**: `GET /api/chat/history`
- **功能**: 分页获取聊天记录。
- **参数**:
    - `before_id` (int, 可选): 获取该 ID 之前的消息（用于向上滚动加载更多）
    - `limit` (int, 默认 20): 获取数量
- **响应**:
    ```json
    {
      "items": [
        {
          "id": 100,
          "sender_id": 1,
          "content": "Hello",
          "timestamp": "2023-10-27 10:00:00",
          "sender_name": "Boy",
          "sender_avatar": "..."
        }
      ],
      "has_more": true
    }
    ```

---

## 3. Socket.IO 事件

### 3.1 客户端发送事件 (Client -> Server)

#### `join`
- **说明**: 加入聊天房间。
- **Payload**: `{ "room": "couple_room" }`

#### `message`
- **说明**: 发送新消息。
- **Payload**: 
    ```json
    {
      "content": "消息内容",
      "sender_id": 1,
      "room": "couple_room"
    }
    ```

#### `typing`
- **说明**: 开始输入状态。
- **Payload**: `{ "sender_id": 1, "room": "couple_room" }`

#### `stop_typing`
- **说明**: 停止输入状态。
- **Payload**: `{ "sender_id": 1, "room": "couple_room" }`

#### `recall`
- **说明**: 撤回消息。
- **Payload**: `{ "id": 100, "sender_id": 1, "room": "couple_room" }`

### 3.2 服务端广播事件 (Server -> Client)

#### `response`
- **说明**: 收到新消息。
- **Payload**:
    ```json
    {
      "id": 101,
      "sender_id": 1,
      "content": "消息内容",
      "timestamp": "2023-10-27 10:01:00",
      "sender_name": "Boy",
      "sender_avatar": "..."
    }
    ```

#### `status_change`
- **说明**: 用户状态变更（输入中/在线）。
- **Payload**: `{ "user_id": 1, "status": "typing" }` (or "online")

#### `message_recalled`
- **说明**: 消息被撤回。
- **Payload**: `{ "id": 100 }`
