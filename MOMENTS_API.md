# Love Plane - 日常动态模块 API 文档

本文档详细描述了日常动态模块 (Moments) 的后端接口实现，包括动态的发布、查询、互动（点赞/评论）及删除功能。

## 1. 数据模型

### User (用户)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | Integer | 主键 |
| name | String | 昵称 |
| avatar | String | 头像 URL |

### Moment (动态)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | Integer | 主键 |
| content | Text | 动态内容 |
| timestamp | DateTime | 发布时间 |
| user_id | Integer | 外键 (关联 User) |
| images_json | Text | 图片路径列表 (JSON Array) |

### Comment (评论)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | Integer | 主键 |
| content | Text | 评论内容 |
| timestamp | DateTime | 评论时间 |
| user_id | Integer | 评论者 ID |
| moment_id | Integer | 关联动态 ID |

### Like (点赞)
| 字段 | 类型 | 说明 |
| :--- | :--- | :--- |
| id | Integer | 主键 |
| user_id | Integer | 点赞者 ID |
| moment_id | Integer | 关联动态 ID |

---

## 2. 接口列表

### 2.1 获取动态列表
- **URL**: `GET /api/moments`
- **功能**: 分页获取动态列表，支持搜索和筛选。
- **参数**:
    - `page` (int, 默认 1): 页码
    - `per_page` (int, 默认 20): 每页数量
    - `user_id` (int, 可选): 筛选特定用户的动态
    - `keyword` (str, 可选): 搜索内容关键词
    - `mode` (str, 默认 'fuzzy'): 'exact' 或 'fuzzy'
- **响应**:
    ```json
    {
      "code": 200,
      "msg": "success",
      "data": {
        "items": [
          {
            "id": 1,
            "content": "...",
            "images": ["/static/uploads/..."],
            "publisher": {"id": 1, "name": "Boy", "avatar": "..."},
            "created_at": "2023-10-01 10:00:00",
            "stats": {"likes": 5, "comments": 2}
          }
        ],
        "pagination": {
          "current_page": 1,
          "total_pages": 5,
          "total_items": 100,
          "has_next": true,
          "has_prev": false
        }
      }
    }
    ```

### 2.2 发布动态
- **URL**: `POST /moments/add`
- **Content-Type**: `multipart/form-data`
- **参数**:
    - `content` (str, 必填): 动态内容
    - `user_id` (int, 必填): 发布者 ID
    - `images` (file, 可选): 多张图片文件
- **响应**: 重定向至 `/moments` 页面。

### 2.3 删除动态
- **URL**: `POST /moments/<id>/delete`
- **响应**:
    ```json
    { "code": 200, "msg": "success" }
    ```

### 2.4 点赞/取消点赞
- **URL**: `POST /moments/<id>/like`
- **Content-Type**: `application/json`
- **Body**:
    ```json
    { "user_id": 1 }
    ```
- **响应**:
    ```json
    { 
      "code": 200, 
      "msg": "success", 
      "action": "liked" // 或 "unliked"
    }
    ```

### 2.5 获取动态评论列表
- **URL**: `GET /api/moments/<id>/comments`
- **功能**: 分页获取指定动态的评论列表。
- **参数**:
    - `page` (int, 默认 1): 页码
    - `per_page` (int, 默认 10): 每页数量
- **响应**:
    ```json
    {
      "code": 200,
      "msg": "success",
      "data": {
        "items": [
          {
            "id": 101,
            "content": "评论内容",
            "user": { "name": "Boy", "avatar": "..." },
            "timestamp": "2023-10-01 10:05:00"
          }
        ],
        "pagination": {
          "current_page": 1,
          "total_pages": 1,
          "total_items": 1,
          "has_next": false,
          "has_prev": false
        }
      }
    }
    ```

### 2.6 发表评论
- **URL**: `POST /moments/<id>/comment`
- **Content-Type**: `application/json`
- **Body**:
    ```json
    { 
      "user_id": 1,
      "content": "评论内容"
    }
    ```
- **响应**:
    ```json
    {
      "code": 200,
      "msg": "success",
      "data": {
        "id": 101,
        "content": "评论内容",
        "user": { "name": "Boy", "avatar": "..." },
        "timestamp": "2023-10-01 10:05:00"
      }
    }
    ```
