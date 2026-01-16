# Love Plane 系统问题与改进需求文档

## 概述

本文档详细记录了当前 Love Plane 系统存在的问题及需要改进的功能需求，包括技术实现建议和优先级评估。

---

## 1. 纪念日显示功能优化

### 问题描述

当前系统在首页显示 5 个最近的纪念日，但实际需求是仅显示两个最重要的纪念日，以提高用户体验和界面简洁性。

### 当前实现分析

**后端代码位置**: [app.py#L87-L91](file:///d:/project/love-plain/love-plain/app.py#L87-L91)

```python
@app.route('/')
def index():
    # Only fetch the 5 most recent anniversaries for the main dashboard
    recent_anniversaries = Anniversary.query.order_by(Anniversary.id.desc()).limit(5).all()
    total_count = Anniversary.query.count()
    return render_template('index.html', anniversaries=recent_anniversaries, total_count=total_count)
```

**前端代码位置**: [index.html#L24-L41](file:///d:/project/love-plain/love-plain/templates/index.html#L24-L41)

当前前端会遍历所有传入的纪念日进行显示。

### 改进需求

1. **后端修改**:
   - 将查询限制从 5 个改为 2 个
   - 定义"最重要"的纪念日排序逻辑（建议按距离今天的天数排序）

2. **前端修改**:
   - 移除"查看全部"按钮（如果只显示2个）
   - 优化移动端和桌面端的显示布局
   - 确保响应式设计适配

3. **排序逻辑建议**:
   - 优先显示即将到来的纪念日（按天数升序）
   - 如果有多个纪念日同一天，按重要性或创建时间排序

### 技术实现建议

#### 后端实现

```python
@app.route('/')
def index():
    # 获取两个最重要的纪念日（按距离今天的天数升序）
    today = date.today()
    important_anniversaries = Anniversary.query.order_by(
        # 计算距离今天的天数差
        func.julianday(Anniversary.date) - func.julianday(today)
    ).limit(2).all()
    
    total_count = Anniversary.query.count()
    return render_template('index.html', anniversaries=important_anniversaries, total_count=total_count)
```

#### 前端实现

- 移除"查看全部"按钮相关代码
- 调整卡片布局，使两个纪念日更加突出
- 添加"查看更多纪念日"的链接，跳转到完整的纪念日列表页面

### 优先级评估

**优先级**: 🔴 高

**理由**:
- 影响首页核心功能展示
- 直接影响用户体验
- 实现相对简单，工作量小

**预计工作量**: 2-3 小时

---

## 2. 用户认证系统改造

### 问题描述

当前系统没有用户认证机制，任何用户都可以访问所有功能。需要实现基于 token 的用户认证系统，确保只有授权用户才能访问系统。

### 当前实现分析

当前系统存在以下问题：
1. 没有登录/登出功能
2. 没有会话管理
3. 所有路由都是公开的
4. 用户身份通过前端选择（如聊天页面中的用户选择器）

### 改进需求

1. **Token 映射规则**:
   - Token `"ck"` 对应男性角色（Boy）
   - Token `"wkl"` 对应女性角色（Girl）

2. **认证流程**:
   - 系统启动时必须先进行 token 验证
   - 验证成功后建立会话
   - 所有需要认证的路由都需要检查 token

3. **会话管理**:
   - 使用 Flask-Login 或自定义 session 管理
   - 实现 token 验证中间件
   - 处理 token 过期和刷新

### 技术实现建议

#### 1. 数据库模型扩展

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(200), default='/static/avatars/default.png')
    token = db.Column(db.String(100), unique=True, nullable=False)  # 新增 token 字段
    role = db.Column(db.String(20), nullable=False)  # 'male' or 'female'
```

#### 2. Token 验证中间件

```python
from functools import wraps
from flask import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = session.get('token')
        if not token or not validate_token(token):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def validate_token(token):
    user = User.query.filter_by(token=token).first()
    return user is not None

def get_current_user():
    token = session.get('token')
    if token:
        return User.query.filter_by(token=token).first()
    return None
```

#### 3. 登录路由

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = request.form.get('token')
        user = User.query.filter_by(token=token).first()
        if user:
            session['token'] = token
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid token')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
```

#### 4. 保护路由

```python
@app.route('/')
@login_required
def index():
    # ... 现有代码

@app.route('/moments')
@login_required
def moments():
    # ... 现有代码

@app.route('/chat')
@login_required
def chat():
    # ... 现有代码
```

#### 5. 初始化 Token 数据

修改 [seed_data.py](file:///d:/project/love-plain/love-plain/seed_data.py) 添加 token:

```python
if User.query.count() == 0:
    print("Seeding Users...")
    boy = User(
        name='Boy', 
        avatar='https://cdn-icons-png.flaticon.com/512/4140/4140048.png',
        token='ck',
        role='male'
    )
    girl = User(
        name='Girl', 
        avatar='https://cdn-icons-png.flaticon.com/512/4140/4140047.png',
        token='wkl',
        role='female'
    )
    db.session.add(boy)
    db.session.add(girl)
    db.session.commit()
    print("Users seeded.")
```

#### 6. 前端登录页面

创建 `templates/login.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-4">
        <div class="card shadow">
            <div class="card-body p-5">
                <h2 class="text-center mb-4">❤️ Love Plane</h2>
                <form method="POST">
                    {% if error %}
                    <div class="alert alert-danger">{{ error }}</div>
                    {% endif %}
                    <div class="mb-3">
                        <label class="form-label">请输入您的 Token</label>
                        <input type="text" name="token" class="form-control" placeholder="输入 token" required>
                    </div>
                    <button type="submit" class="btn btn-danger w-100">登录</button>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 优先级评估

**优先级**: 🔴 高

**理由**:
- 系统安全性核心功能
- 影响所有功能的访问控制
- 用户隐私保护的基础

**预计工作量**: 6-8 小时

---

## 3. 日常功能显示问题

### 问题描述

当前日常动态页面中，用户头像和名字可能无法正确显示，需要检查数据获取接口和前端渲染逻辑。此外，日常功能的显示和发送需要使用当前会话 token 认证后的身份，而不是通过前端选择或硬编码用户ID。

### 当前实现分析

**后端代码位置**: [app.py#L154-L178](file:///d:/project/love-plain/love-plain/app.py#L154-L178)

```python
items = []
for m in pagination.items:
    items.append({
        'id': m.id,
        'content': m.content,
        'images': m.images,
        'publisher': {
            'id': m.user.id,
            'name': m.user.name,
            'avatar': m.user.avatar
        },
        'created_at': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'stats': {
            'likes': len(m.likes),
            'comments': len(m.comments)
        },
    })
```

**前端代码位置**: [moments.html#L331-L334](file:///d:/project/love-plain/love-plain/templates/moments.html#L331-L334)

```javascript
clone.querySelector('.user-name').textContent = item.publisher.name;
clone.querySelector('.user-avatar').src = item.publisher.avatar;
```

**发送功能分析**: 
- 发送动态: [app.py#L191-L222](file:///d:/project/love-plain/love-plain/app.py#L191-L222) 和 [moments.html#L64-L82](file:///d:/project/love-plain/love-plain/templates/moments.html#L64-L82)
- 发送评论: [app.py#L235-L254](file:///d:/project/love-plain/love-plain/app.py#L235-L254) 和 [moments.html#L409-L425](file:///d:/project/love-plain/love-plain/templates/moments.html#L409-L425)
- 点赞功能: [app.py#L224-L233](file:///d:/project/love-plain/love-plain/app.py#L224-L233) 和 [moments.html#L362-L372](file:///d:/project/love-plain/love-plain/templates/moments.html#L362-L372)

当前实现中，发送动态和评论时用户身份由前端传递，点赞等功能也使用硬编码的用户ID。

### 改进需求

1. **身份认证**:
   - 发布动态时自动使用当前会话认证后的用户身份
   - 发布评论时自动使用当前会话认证后的用户身份
   - 点赞功能应使用当前会话认证后的用户身份

2. **前端修改**:
   - 移除手动选择用户身份的下拉框
   - 自动获取当前认证用户信息用于界面显示
   - 确保所有交互操作都使用正确的用户身份

3. **后端修改**:
   - 在API端点中使用get_current_user()获取当前用户
   - 验证用户权限以执行特定操作

### 技术实现建议

#### 1. 后端数据验证

添加数据验证和错误处理，同时获取当前认证用户：

```python
@app.route('/api/moments')
def get_moments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', type=int)
    keyword = request.args.get('keyword', type=str)
    mode = request.args.get('mode', 'fuzzy')
    
    query = Moment.query.options(
        db.joinedload(Moment.user)  # 预加载用户数据
    ).order_by(Moment.timestamp.desc())
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if keyword:
        if mode == 'exact':
             query = query.filter(Moment.content == keyword)
        else:
             query = query.filter(Moment.content.like(f'%{keyword}%'))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    items = []
    for m in pagination.items:
        # 验证用户数据是否存在
        if not m.user:
            print(f"Warning: Moment {m.id} has no associated user")
            continue
            
        items.append({
            'id': m.id,
            'content': m.content,
            'images': m.images,
            'publisher': {
                'id': m.user.id,
                'name': m.user.name or 'Unknown User',
                'avatar': m.user.avatar or '/static/avatars/default.png'
            },
            'created_at': m.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'stats': {
                'likes': len(m.likes),
                'comments': len(m.comments)
            },
        })
        
    return {
        'code': 200,
        'msg': 'success',
        'data': {
            'items': items,
            'pagination': {
                'current_page': page,
                'total_pages': pagination.pages,
                'total_items': pagination.total,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    }
```

#### 2. 动态发布功能修改

修改动态发布API以使用当前认证用户身份：

```python
@app.route('/moments/add', methods=['POST'])
@login_required
def add_moment():
    content = request.form.get('content')
    # 从当前会话获取用户身份，不再接受前端传递的user_id
    current_user = get_current_user()
    if not current_user:
        return {'code': 401, 'msg': 'Authentication required'}, 401
    
    if not content:
        return {'code': 400, 'msg': 'Content is required'}, 400
        
    image_paths = []
    if 'images' in request.files:
        files = request.files.getlist('images')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid collision
                timestamp_str = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp_str}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_paths.append(f"/static/uploads/{filename}")
    
    moment = Moment(content=content, user_id=current_user.id)
    moment.images = image_paths
    
    db.session.add(moment)
    db.session.commit()
    
    return redirect(url_for('moments'))
```

#### 3. 评论功能修改

修改评论API以使用当前认证用户身份：

```python
@app.route('/moments/<int:id>/comment', methods=['POST'])
@login_required
def comment_moment(id):
    content = request.json.get('content')
    # 从当前会话获取用户身份
    current_user = get_current_user()
    if not current_user:
        return {'code': 401, 'msg': 'Authentication required'}, 401
    
    if not content:
         return {'code': 400, 'msg': 'Content is required'}, 400
         
    comment = Comment(content=content, user_id=current_user.id, moment_id=id)
    db.session.add(comment)
    db.session.commit()
    
    return {'code': 200, 'msg': 'success', 'data': {
        'id': comment.id,
        'content': comment.content,
        'user': {
            'name': comment.user.name,
            'avatar': comment.user.avatar
        },
        'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }}
```

#### 4. 点赞功能修改

修改点赞API以使用当前认证用户身份：

```python
@app.route('/moments/<int:id>/like', methods=['POST'])
@login_required
def like_moment(id):
    # 从当前会话获取用户身份
    current_user = get_current_user()
    if not current_user:
        return {'code': 401, 'msg': 'Authentication required'}, 401
    
    existing_like = Like.query.filter_by(user_id=current_user.id, moment_id=id).first()
    if existing_like:
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        new_like = Like(user_id=current_user.id, moment_id=id)
        db.session.add(new_like)
        action = 'liked'
        
    db.session.commit()
    return {'code': 200, 'msg': 'success', 'action': action}
```

#### 2. 前端错误处理

添加前端数据验证和错误处理，以及获取当前认证用户信息：

```javascript
document.addEventListener('DOMContentLoaded', function() {
    let currentPage = 1;
    let isLoading = false;
    let hasMore = true;
    const momentsList = document.getElementById('momentsList');
    const loadingSpinner = document.getElementById('loading');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    const loadMoreContainer = document.getElementById('loadMoreContainer');
    const noMoreData = document.getElementById('noMoreData');
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const userFilter = document.getElementById('userFilter');
    const commentTemplate = document.getElementById('commentItemTemplate');
    
    // 获取当前认证用户信息
    let currentUser = null;
    fetch('/api/user/info')
        .then(response => response.json())
        .then(data => {
            if (data.code === 200) {
                currentUser = data.data;
                // 可以在这里更新界面显示当前用户信息
                updateCurrentUserUI(currentUser);
            }
        })
        .catch(err => {
            console.error('Failed to get user info:', err);
        });
    
    // 更新当前用户界面
    function updateCurrentUserUI(user) {
        // 例如，在发布按钮附近显示当前用户名
        const publishModal = document.getElementById('publishModal');
        const publishForm = publishModal.querySelector('form');
        // 移除用户选择下拉框，因为我们现在自动使用当前认证用户
        const userIdSelect = publishForm.querySelector('select[name="user_id"]');
        if (userIdSelect) {
            userIdSelect.closest('.mb-3').remove();
        }
    }
    
    // Initial Load
    loadMoments();
    
    // Search
    searchBtn.addEventListener('click', () => {
        resetList();
        loadMoments();
    });
    
    // Load More
    loadMoreBtn.addEventListener('click', () => {
        loadMoments();
    });
    
    function resetList() {
        momentsList.innerHTML = '';
        currentPage = 1;
        hasMore = true;
        noMoreData.classList.add('d-none');
    }
    
    function loadMoments() {
        if (isLoading || !hasMore) return;
        
        isLoading = true;
        loadingSpinner.classList.remove('d-none');
        loadMoreContainer.classList.add('d-none');
        
        const keyword = searchInput.value;
        const userId = userFilter.value;
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 5, // Load 5 at a time for demo
            keyword: keyword,
            user_id: userId
        });
        
        fetch(`/api/moments?${params}`)
            .then(response => response.json())
            .then(data => {
                if (data.code === 200) {
                    const items = data.data.items;
                    if (items.length === 0) {
                        hasMore = false;
                        if (currentPage === 1) {
                            momentsList.innerHTML = '<div class="text-center text-muted py-5">暂无动态</div>';
                        } else {
                            noMoreData.classList.remove('d-none');
                        }
                    } else {
                        renderMoments(items);
                        if (!data.data.pagination.has_next) {
                            hasMore = false;
                            noMoreData.classList.remove('d-none');
                        } else {
                            currentPage++;
                            loadMoreContainer.classList.remove('d-none');
                        }
                    }
                }
            })
            .catch(err => {
                console.error('Error:', err);
                alert('加载失败');
            })
            .finally(() => {
                isLoading = false;
                loadingSpinner.classList.add('d-none');
            });
    }
    
    function renderMoments(items) {
        const template = document.getElementById('momentTemplate');
        
        items.forEach(item => {
            const clone = template.content.cloneNode(true);
            const card = clone.querySelector('.moment-item');
            
            // User Info with fallback
            const userName = item.publisher.name || 'Unknown User';
            const userAvatar = item.publisher.avatar || '/static/avatars/default.png';
            
            clone.querySelector('.user-name').textContent = userName;
            clone.querySelector('.user-avatar').src = userAvatar;
            clone.querySelector('.user-avatar').onerror = function() {
                this.src = '/static/avatars/default.png';
            };
            clone.querySelector('.created-at').textContent = item.created_at;
            
            // Content
            clone.querySelector('.content-text').textContent = item.content;
            
            // Images
            const imgContainer = clone.querySelector('.images-container');
            if (item.images && item.images.length > 0) {
                item.images.forEach(imgSrc => {
                    const col = document.createElement('div');
                    col.className = 'col-4';
                    col.innerHTML = `<img src="${imgSrc}" class="img-fluid rounded" style="object-fit: cover; width: 100%; height: 100px; cursor: pointer;" onclick="window.open('${imgSrc}')">`;
                    imgContainer.appendChild(col);
                });
            } else {
                imgContainer.remove();
            }
            
            // Stats
            const likesCountEl = clone.querySelector('.likes-count');
            likesCountEl.textContent = item.stats.likes;
            
            const commentsCountEl = clone.querySelector('.comments-count');
            commentsCountEl.textContent = item.stats.comments;
            
            // Actions
            const likeBtn = clone.querySelector('.like-btn');
            likeBtn.addEventListener('click', () => {
                fetch(`/moments/${item.id}/like`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                    // 不再传递user_id，因为后端会从会话中获取
                })
                .then(res => res.json())
                .then(res => {
                    if (res.code === 200) {
                        let current = parseInt(likesCountEl.textContent);
                        if (res.action === 'liked') likesCountEl.textContent = current + 1;
                        else likesCountEl.textContent = current - 1;
                    }
                });
            });
            
            // Delete button - only show for current user's posts
            const deleteBtn = clone.querySelector('.delete-btn');
            if (currentUser && currentUser.id === item.publisher.id) {
                deleteBtn.parentElement.style.display = 'block';
                deleteBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    if(confirm('确定删除这条动态吗？')) {
                        fetch(`/moments/${item.id}/delete`, {method: 'POST'})
                        .then(res => res.json())
                        .then(res => {
                            if(res.code === 200) {
                                card.remove();
                            }
                        });
                    }
                });
            } else {
                // Hide delete option for other users' posts
                deleteBtn.parentElement.style.display = 'none';
            }
            
            // Comments Toggle
            const commentBtn = clone.querySelector('.comment-btn');
            const commentsSection = clone.querySelector('.comments-section');
            const commentsListEl = clone.querySelector('.comments-list');
            const loadMoreCommentsBtn = clone.querySelector('.load-more-comments-btn');
            const loadMoreCommentsContainer = clone.querySelector('.load-more-comments-container');
            let commentsPage = 1;
            let commentsLoaded = false;
            
            commentBtn.addEventListener('click', () => {
                const isHidden = commentsSection.classList.contains('d-none');
                commentsSection.classList.toggle('d-none');
                
                if (isHidden && !commentsLoaded) {
                    loadComments(item.id, 1);
                }
            });

            loadMoreCommentsBtn.addEventListener('click', () => {
                loadComments(item.id, commentsPage + 1);
            });

            function loadComments(momentId, page) {
                loadMoreCommentsBtn.textContent = '加载中...';
                loadMoreCommentsBtn.disabled = true;

                fetch(`/api/moments/${momentId}/comments?page=${page}&per_page=10`)
                    .then(res => res.json())
                    .then(res => {
                        if (res.code === 200) {
                            commentsPage = page;
                            const items = res.data.items;
                            
                            if (page === 1) {
                                commentsListEl.innerHTML = '';
                            }

                            items.forEach(comment => {
                                renderComment(comment, commentsListEl);
                            });
                            
                            commentsLoaded = true;

                            // Handle pagination button
                            if (res.data.pagination.has_next) {
                                loadMoreCommentsContainer.classList.remove('d-none');
                                loadMoreCommentsBtn.textContent = '查看更多评论';
                                loadMoreCommentsBtn.disabled = false;
                            } else {
                                loadMoreCommentsContainer.classList.add('d-none');
                            }
                            
                            // Update count if needed, though usually we trust the list stats
                        }
                    })
                    .catch(err => {
                        console.error('Failed to load comments:', err);
                        loadMoreCommentsBtn.textContent = '加载失败';
                    });
            }
            
            function renderComment(comment, container) {
                const commentClone = commentTemplate.content.cloneNode(true);
                commentClone.querySelector('.comment-avatar').src = comment.user.avatar;
                commentClone.querySelector('.comment-user-name').textContent = comment.user.name;
                commentClone.querySelector('.comment-time').textContent = comment.timestamp;
                commentClone.querySelector('.comment-content').textContent = comment.content;
                container.appendChild(commentClone);
            }
            
            // Send Comment
            const sendBtn = clone.querySelector('.send-comment-btn');
            const commentInput = clone.querySelector('.comment-input');
            
            sendBtn.addEventListener('click', () => {
                const content = commentInput.value.trim();
                if (!content) return;
                
                sendBtn.disabled = true;
                sendBtn.textContent = '发送中...';

                fetch(`/moments/${item.id}/comment`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        content: content
                        // 不再传递user_id，因为后端会从会话中获取
                    })
                })
                .then(res => res.json())
                .then(res => {
                    if (res.code === 200) {
                        commentInput.value = '';
                        commentsCountEl.textContent = parseInt(commentsCountEl.textContent) + 1;
                        
                        // Append the new comment
                        renderComment(res.data, commentsListEl);
                        
                        // If list was hidden or empty, ensure it's shown
                        if (commentsSection.classList.contains('d-none')) {
                            commentsSection.classList.remove('d-none');
                        }
                    }
                })
                .finally(() => {
                    sendBtn.disabled = false;
                    sendBtn.textContent = '发送';
                });
            });

            momentsList.appendChild(clone);
        });
    }
});
```

#### 3. 数据库修复脚本

创建修复脚本 `fix_moments.py`:

```python
from app import app, db, Moment, User

def fix_orphaned_moments():
    with app.app_context():
        # 查找没有关联用户的 Moment
        orphaned = Moment.query.filter(~Moment.user_id.in_(
            db.session.query(User.id)
        )).all()
        
        print(f"Found {len(orphaned)} orphaned moments")
        
        # 删除或重新分配
        for moment in orphaned:
            print(f"Deleting moment {moment.id}")
            db.session.delete(moment)
        
        db.session.commit()
        print("Fix complete!")

if __name__ == "__main__":
    fix_orphaned_moments()
```

#### 4. 添加默认头像

确保默认头像文件存在：

```python
# 在 app.py 初始化时检查
DEFAULT_AVATAR_PATH = 'static/avatars/default.png'
if not os.path.exists(DEFAULT_AVATAR_PATH):
    os.makedirs(os.path.dirname(DEFAULT_AVATAR_PATH), exist_ok=True)
    # 创建一个简单的默认头像或从外部下载
```

### 优先级评估

**优先级**: 🟡 中

**理由**:
- 影响用户体验但不影响核心功能
- 可能是数据问题而非代码问题
- 需要先诊断具体原因
- 现在还包括了身份认证集成，增加了重要性

**预计工作量**: 4-6 小时

---

## 4. 日常功能发送身份认证集成

### 问题描述

当前日常功能的发送（发布动态、评论、点赞）需要集成身份认证，使用当前会话 token 认证后的身份，而不是通过前端选择或硬编码用户ID。

### 当前实现分析

**前端发布表单位置**: [moments.html#L64-L82](file:///d:/project/love-plain/love-plain/templates/moments.html#L64-L82)

当前实现中，发布动态时前端会提供一个用户选择下拉框，这与认证系统的设计不符。

### 改进需求

1. **前端表单修改**:
   - 移除发布动态表单中的用户选择下拉框
   - 使用JavaScript自动获取当前认证用户信息用于界面显示

2. **后端验证**:
   - 确保所有发送操作都验证当前认证用户的身份
   - 防止用户冒充其他身份进行操作

### 技术实现建议

#### 1. 前端发布动态表单修改

修改前端发布动态的表单，移除用户选择下拉框，并确保使用当前认证的用户身份：

```html
<!-- Publish Modal -->
<div class="modal fade" id="publishModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">发布新动态</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form id="publishForm" action="/moments/add" method="POST" enctype="multipart/form-data">
                <div class="modal-body">
                    <!-- 用户身份现在通过后端会话自动获取，不需要前端选择 -->
                    <div class="mb-3">
                        <textarea name="content" class="form-control" rows="4" placeholder="今天发生了什么..." required></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">添加图片 (可选)</label>
                        <input type="file" name="images" class="form-control" multiple accept="image/*">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                    <button type="submit" class="btn btn-primary">发布</button>
                </div>
            </form>
        </div>
    </div>
</div>
```

#### 2. 前端JavaScript增强

为了更好地处理当前用户身份，我们可以增强JavaScript代码：

```javascript
// 在现有JavaScript代码中添加表单提交处理
const publishForm = document.getElementById('publishForm');
if (publishForm) {
    publishForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 由于后端会自动获取当前用户身份，我们只需提交内容
        const formData = new FormData(this);
        
        fetch('/moments/add', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then(data => {
            if (data && data.code !== 200) {
                alert('发布失败: ' + (data.msg || '未知错误'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('发布失败，请重试');
        });
    });
}
```

### 优先级评估

**优先级**: 🟡 中

**理由**:
- 与用户认证系统紧密相关，需要同步实施
- 提高系统安全性，防止身份伪造
- 改善用户体验，无需手动选择身份

**预计工作量**: 2-3 小时

---

## 5. 功能替换需求：AI 每日播报

### 问题描述

需要将现有的"亲密聊天"功能替换为 AI 每日播报功能。新功能将集成大语言模型 API，自动生成关于日常和纪念日的语音播报。

### 当前实现分析

**现有聊天功能**:
- 基于 WebSocket 的实时聊天
- 代码位置: [app.py#L311-L371](file:///d:/project/love-plain/love-plain/app.py#L311-L371)
- 前端页面: [chat.html](file:///d:/project/love-plain/love-plain/templates/chat.html)

### 改进需求

1. **AI 每日播报功能要求**:
   - 集成大语言模型 API（如 OpenAI GPT、文心一言等）
   - 自动分析日常动态和纪念日
   - 生成个性化的播报内容
   - 支持语音播报（TTS）
   - 设计友好的播报界面和交互流程

2. **播报内容**:
   - 今日纪念日提醒
   - 最近重要动态摘要
   - 情感化的话语和祝福
   - 个性化的建议和提醒

3. **交互流程**:
   - 用户点击"生成今日播报"
   - 系统收集数据并调用 AI API
   - 生成播报文本
   - 转换为语音并播放
   - 显示播报文本供阅读

### 技术实现建议

#### 1. 后端实现

##### 1.1 添加 AI 配置

在 `.env` 文件中添加：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo
```

##### 1.2 创建 AI 服务模块

创建 `ai_service.py`:

```python
import openai
import os
from datetime import date, datetime, timedelta
from app import app, db, Anniversary, Moment

openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')

class AIDailyReportService:
    
    @staticmethod
    def collect_daily_data():
        """收集今日播报所需的数据"""
        today = date.today()
        
        # 获取即将到来的纪念日（未来7天内）
        upcoming_anniversaries = Anniversary.query.filter(
            Anniversary.date >= today,
            Anniversary.date <= today + timedelta(days=7)
        ).order_by(Anniversary.date).all()
        
        # 获取最近的动态（过去3天内），并限制为当前认证用户
        three_days_ago = datetime.now() - timedelta(days=3)
        recent_moments = Moment.query.filter(
            Moment.timestamp >= three_days_ago
        ).order_by(Moment.timestamp.desc()).limit(10).all()
        
        return {
            'today': today.strftime('%Y年%m月%d日'),
            'upcoming_anniversaries': upcoming_anniversaries,
            'recent_moments': recent_moments
        }
    
    @staticmethod
    def generate_report_text(data):
        """使用 AI 生成播报文本"""
        
        # 构建纪念日信息
        anniversary_info = []
        for ann in data['upcoming_anniversaries']:
            days_until = (ann.date - date.today()).days
            if days_until == 0:
                anniversary_info.append(f"今天是{ann.title}！")
            else:
                anniversary_info.append(f"还有{days_until}天就是{ann.title}了")
        
        # 构建动态信息
        moment_info = []
        for moment in data['recent_moments']:
            moment_info.append(f"{moment.user.name}说：{moment.content[:50]}...")
        
        # 构建 AI 提示词
        prompt = f"""
请以温柔、浪漫的语气，为情侣生成一份每日播报。

今天是{data['today']}。

纪念日信息：
{chr(10).join(anniversary_info) if anniversary_info else '近期没有特别的纪念日'}

最近动态：
{chr(10).join(moment_info) if moment_info else '最近没有新的动态'}

请生成一份温馨的播报，包含：
1. 亲切的问候
2. 纪念日提醒（如果有）
3. 动态摘要（如果有）
4. 一句浪漫的话或祝福

播报要自然流畅，像是在和恋人说话一样。
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=os.getenv('AI_MODEL', 'gpt-3.5-turbo'),
                messages=[
                    {"role": "system", "content": "你是一个温柔浪漫的助手，专门为情侣生成每日播报。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"AI API Error: {e}")
            return AIDailyReportService.generate_fallback_report(data)
    
    @staticmethod
    def generate_fallback_report(data):
        """生成备用播报文本（当 AI API 不可用时）"""
        report_parts = [f"亲爱的，今天是{data['today']}。"]
        
        if data['upcoming_anniversaries']:
            report_parts.append("即将到来的纪念日有：")
            for ann in data['upcoming_anniversaries']:
                days_until = (ann.date - date.today()).days
                report_parts.append(f"- {ann.title}（还有{days_until}天）")
        
        if data['recent_moments']:
            report_parts.append("最近的动态：")
            for moment in data['recent_moments'][:3]:
                report_parts.append(f"- {moment.user.name}：{moment.content[:30]}...")
        
        report_parts.append("希望今天也是美好的一天！❤️")
        
        return "\n".join(report_parts)
    
    @staticmethod
    def text_to_speech(text, output_file='static/reports/daily_report.mp3'):
        """将文本转换为语音"""
        try:
            # 使用 edge-tts 或其他 TTS 服务
            # 这里以 edge-tts 为例
            import edge_tts
            
            communicate = edge_tts.Communicate(text, 'zh-CN-XiaoxiaoNeural')
            await communicate.save(output_file)
            
            return output_file
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
```

##### 1.3 添加播报路由

在 `app.py` 中添加：

```python
from ai_service import AIDailyReportService

@app.route('/daily-report')
@login_required
def daily_report():
    return render_template('daily_report.html')

@app.route('/api/daily-report/generate', methods=['POST'])
@login_required
def generate_daily_report():
    try:
        data = AIDailyReportService.collect_daily_data()
        report_text = AIDailyReportService.generate_report_text(data)
        
        # 保存播报到数据库（可选）
        # daily_report = DailyReport(content=report_text, date=date.today())
        # db.session.add(daily_report)
        # db.session.commit()
        
        return {
            'code': 200,
            'msg': 'success',
            'data': {
                'text': report_text,
                'date': data['today']
            }
        }
    except Exception as e:
        print(f"Error generating report: {e}")
        return {
            'code': 500,
            'msg': f'生成播报失败: {str(e)}'
        }, 500

@app.route('/api/daily-report/tts', methods=['POST'])
@login_required
def generate_report_tts():
    text = request.json.get('text')
    if not text:
        return {'code': 400, 'msg': 'Text is required'}, 400
    
    try:
        audio_file = AIDailyReportService.text_to_speech(text)
        if audio_file:
            return {
                'code': 200,
                'msg': 'success',
                'data': {
                    'audio_url': '/' + audio_file
                }
            }
        else:
            return {
                'code': 500,
                'msg': '语音生成失败'
            }, 500
    except Exception as e:
        print(f"TTS Error: {e}")
        return {
            'code': 500,
            'msg': f'语音生成失败: {str(e)}'
        }, 500
```

#### 2. 前端实现

创建 `templates/daily_report.html`:

```html
{% extends "base.html" %}

{% block content %}
<style>
    .report-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .report-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
    }
    .report-text {
        font-size: 1.2rem;
        line-height: 1.8;
        white-space: pre-wrap;
    }
    .audio-player {
        background: rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
    }
    .generate-btn {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border: none;
        border-radius: 50px;
        padding: 15px 40px;
        color: white;
        font-size: 1.1rem;
        transition: all 0.3s;
    }
    .generate-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4);
    }
    .loading-spinner {
        display: none;
    }
    .loading-spinner.active {
        display: inline-block;
    }
</style>

<div class="report-container">
    <div class="text-center mb-5">
        <h1 class="display-5 fw-bold mb-3">🎙️ AI 每日播报</h1>
        <p class="lead text-muted">让 AI 为你生成今日的温馨播报</p>
    </div>

    <div class="card report-card">
        <div class="text-center mb-4">
            <div id="dateDisplay" class="h4 mb-3"></div>
            <button id="generateBtn" class="generate-btn">
                <span class="btn-text">✨ 生成今日播报</span>
                <span class="loading-spinner spinner-border spinner-border-sm ms-2"></span>
            </button>
        </div>

        <div id="reportContent" class="d-none">
            <div class="report-text" id="reportText"></div>
            
            <div class="audio-player">
                <div class="d-flex align-items-center justify-content-between">
                    <div>
                        <h5 class="mb-2">🎧 语音播报</h5>
                        <audio id="audioPlayer" controls class="w-100">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                    <button id="playTTSBtn" class="btn btn-light btn-sm ms-3">
                        🔊 播放语音
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="text-center mt-4">
        <button id="refreshBtn" class="btn btn-outline-secondary">
            🔄 重新生成
        </button>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        const generateBtn = document.getElementById('generateBtn');
        const refreshBtn = document.getElementById('refreshBtn');
        const reportContent = document.getElementById('reportContent');
        const reportText = document.getElementById('reportText');
        const audioPlayer = document.getElementById('audioPlayer');
        const playTTSBtn = document.getElementById('playTTSBtn');
        const dateDisplay = document.getElementById('dateDisplay');
        const btnText = generateBtn.querySelector('.btn-text');
        const spinner = generateBtn.querySelector('.loading-spinner');

        // 显示当前日期
        const today = new Date();
        const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' };
        dateDisplay.textContent = today.toLocaleDateString('zh-CN', options);

        let currentReportText = '';

        generateBtn.addEventListener('click', generateReport);
        refreshBtn.addEventListener('click', generateReport);
        playTTSBtn.addEventListener('click', playTTS);

        async function generateReport() {
            btnText.textContent = '生成中...';
            spinner.classList.add('active');
            generateBtn.disabled = true;
            reportContent.classList.add('d-none');

            try {
                const response = await fetch('/api/daily-report/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const result = await response.json();

                if (result.code === 200) {
                    currentReportText = result.data.text;
                    reportText.textContent = currentReportText;
                    reportContent.classList.remove('d-none');
                    
                    // 自动生成语音
                    await generateTTS(currentReportText);
                } else {
                    alert('生成失败: ' + result.msg);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('生成失败，请重试');
            } finally {
                btnText.textContent = '✨ 生成今日播报';
                spinner.classList.remove('active');
                generateBtn.disabled = false;
            }
        }

        async function generateTTS(text) {
            try {
                const response = await fetch('/api/daily-report/tts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });
                const result = await response.json();

                if (result.code === 200) {
                    audioPlayer.src = result.data.audio_url;
                }
            } catch (error) {
                console.error('TTS Error:', error);
            }
        }

        function playTTS() {
            if (audioPlayer.src) {
                audioPlayer.play();
            } else {
                alert('请先生成播报');
            }
        }
    });
</script>
{% endblock %}
```

#### 3. 更新首页

修改 [index.html](file:///d:/project/love-plain/love-plain/templates/index.html)，将聊天卡片替换为播报卡片：

```html
<!-- AI 每日播报板块 -->
<div class="col-md-4">
    <div class="card love-card mb-4 shadow-sm border-0 h-100">
        <div class="card-body text-center">
            <div class="mb-3 display-1">🎙️</div>
            <h3 class="card-title">AI 每日播报</h3>
            <p class="card-text text-muted">听听今天有什么特别的事</p>
            <a href="/daily-report" class="btn btn-success w-100">生成播报</a>
        </div>
    </div>
</div>
```

#### 4. 依赖安装

在 `requirements.txt` 中添加：

```txt
openai>=1.0.0
edge-tts>=6.1.0
```

### 优先级评估

**优先级**: 🟡 中

**理由**:
- 新功能开发，不影响现有功能
- 需要外部 API 集成，有依赖风险
- 可以分阶段实现（先文本，后语音）

**预计工作量**: 12-16 小时

---

## 6. 实施建议

### 实施顺序

建议按照以下顺序实施各项改进：

1. **第一阶段**（高优先级）:
   - 纪念日显示功能优化（2-3 小时）
   - 用户认证系统改造（6-8 小时）

2. **第二阶段**（中优先级）:
   - 日常功能显示问题修复（4-6 小时）
   - 日常功能发送身份认证集成（2-3 小时）
   - AI 每日播报功能开发（12-16 小时）

### 风险评估

| 功能 | 风险等级 | 风险描述 | 缓解措施 |
|------|---------|---------|---------|
| 纪念日优化 | 🟢 低 | 可能影响用户体验 | 充分测试，提供回退方案 |
| 用户认证 | 🟡 中 | 可能导致现有功能无法访问 | 分阶段实施，保留测试账号 |
| 日常显示修复 | 🟢 低 | 可能是数据问题 | 先诊断，再修复 |
| 日常功能身份认证 | 🟡 中 | 可能影响现有功能的用户身份处理 | 逐步迁移，保留兼容性 |
| AI 每日播报 | 🔴 高 | API 依赖、成本控制 | 实现备用方案，监控使用量 |

### 测试建议

1. **单元测试**:
   - Token 验证逻辑
   - AI 服务的数据收集和文本生成
   - 数据库查询优化

2. **集成测试**:
   - 完整的登录流程
   - 认证保护的路由
   - AI 播报生成和播放

3. **用户测试**:
   - 移动端和桌面端响应式测试
   - 不同浏览器的兼容性测试
   - 用户体验测试

---

## 7. 总结

本文档详细记录了 Love Plane 系统的五个主要问题和改进需求：

1. **纪念日显示功能优化** - 简化首页显示，提高用户体验
2. **用户认证系统改造** - 增强系统安全性和用户隐私保护
3. **日常功能显示问题** - 修复用户信息显示问题
4. **日常功能发送身份认证集成** - 使用当前会话认证身份，提升安全性
5. **AI 每日播报功能** - 替换聊天功能，增加智能化特性

所有改进都提供了详细的技术实现建议、代码示例和优先级评估，为后续开发工作提供了清晰的指导。

---

**文档版本**: 1.1  
**创建日期**: 2026-01-16  
**最后更新**: 2026-01-16
